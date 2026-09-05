"""Trusted model loading and deterministic directory checksum.

Security contract:
- The only public entry point is load_trusted_spacy_model().
- No caller may pass a filesystem path; only model_id is accepted.
- All path resolution happens internally and is confined to MODEL_ARTIFACT_ROOT.
- Paths are never included in raised exceptions or return values.
- SHA-256 is computed deterministically before spacy.load() is called.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import Session

from apps.backend.app.core.config import settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public structured status codes
# ---------------------------------------------------------------------------
STATUS_READY = "READY"
STATUS_MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
STATUS_MODEL_NOT_READY = "MODEL_NOT_READY"
STATUS_ARTIFACT_MISSING = "ARTIFACT_MISSING"
STATUS_ARTIFACT_CHECKSUM_INVALID = "ARTIFACT_CHECKSUM_INVALID"
STATUS_ARTIFACT_PATH_REJECTED = "ARTIFACT_PATH_REJECTED"
STATUS_MODEL_INCOMPATIBLE = "MODEL_INCOMPATIBLE"
STATUS_PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
STATUS_FAILED = "FAILED"

# Allow-list for model_id format: alphanumeric, underscores, hyphens only.
_MODEL_ID_RE = re.compile(r'^[a-zA-Z0-9_\-]{1,100}$')

# Files excluded from the deterministic checksum
_EXCLUDE_PATTERNS = frozenset({
    '__pycache__',
    '.DS_Store',
    'Thumbs.db',
})
_EXCLUDE_SUFFIXES = frozenset({
    '.pyc',
    '.pyo',
    '.log',
    '.tmp',
    '.temp',
    '.swp',
})


class ModelLoadError(Exception):
    """Raised when the trusted model load sequence fails.

    Always carries a structured status code.  The message is safe to surface
    (no filesystem paths, no secrets, no raw tracebacks).
    """

    def __init__(self, status: str, safe_message: str) -> None:
        super().__init__(safe_message)
        self.status = status
        self.safe_message = safe_message


# ---------------------------------------------------------------------------
# Model ID validation
# ---------------------------------------------------------------------------

def validate_model_id(model_id: str) -> None:
    """Raise ModelLoadError if model_id does not match the allow-list format."""
    if not model_id or not _MODEL_ID_RE.match(model_id):
        raise ModelLoadError(
            STATUS_ARTIFACT_PATH_REJECTED,
            "Invalid model_id format. Only alphanumeric characters, hyphens, and "
            "underscores are permitted.",
        )


# ---------------------------------------------------------------------------
# Deterministic directory checksum
# ---------------------------------------------------------------------------

def _is_excluded(rel_path: Path) -> bool:
    """Return True if a relative path component matches the exclusion list."""
    for part in rel_path.parts:
        if part in _EXCLUDE_PATTERNS:
            return True
    return rel_path.suffix in _EXCLUDE_SUFFIXES


def compute_directory_checksum(artifact_dir: Path, trusted_root: Path) -> str:
    """Compute a deterministic SHA-256 checksum over a model artifact directory.

    The digest covers:
    - The normalized relative path of each included file (relative to artifact_dir).
    - The raw byte contents of each included file.

    Files are processed in lexicographic order of their normalized relative paths
    to ensure reproducibility across platforms and runs.

    Raises:
        ModelLoadError: if the directory is outside trusted_root, contains
            symlinks that escape trusted_root, is empty of eligible files,
            or does not exist.
    """
    # Resolve both paths to canonical absolute paths
    try:
        resolved_root = trusted_root.resolve(strict=True)
    except (OSError, RuntimeError):
        raise ModelLoadError(
            STATUS_ARTIFACT_PATH_REJECTED,
            "Trusted artifact root could not be resolved.",
        )

    try:
        resolved_dir = artifact_dir.resolve(strict=True)
    except (OSError, RuntimeError):
        raise ModelLoadError(
            STATUS_ARTIFACT_MISSING,
            "Model artifact directory does not exist or cannot be accessed.",
        )

    # Path containment check: artifact_dir must be under trusted_root
    try:
        resolved_dir.relative_to(resolved_root)
    except ValueError:
        raise ModelLoadError(
            STATUS_ARTIFACT_PATH_REJECTED,
            "Model artifact is not within the trusted artifact root.",
        )

    if not resolved_dir.is_dir():
        raise ModelLoadError(
            STATUS_ARTIFACT_MISSING,
            "Model artifact path is not a directory.",
        )

    # Enumerate all files recursively
    eligible_files: list[tuple[str, Path]] = []
    for entry in resolved_dir.rglob("*"):
        # Reject symbolic links that escape the trusted root
        if entry.is_symlink():
            try:
                link_target = entry.resolve(strict=True)
                link_target.relative_to(resolved_root)
            except (ValueError, OSError):
                raise ModelLoadError(
                    STATUS_ARTIFACT_PATH_REJECTED,
                    "Model artifact contains a symbolic link outside the trusted root.",
                )
            # If the link is safe, treat it as a regular file below
            if not entry.is_file():
                continue  # skip symlinks to directories

        if not entry.is_file():
            continue

        rel = entry.relative_to(resolved_dir)
        if _is_excluded(rel):
            continue

        # Normalize path separator to forward slash for cross-platform reproducibility
        normalized_rel = rel.as_posix()
        eligible_files.append((normalized_rel, entry))

    if not eligible_files:
        raise ModelLoadError(
            STATUS_ARTIFACT_MISSING,
            "Model artifact directory contains no eligible files.",
        )

    # Sort by normalized relative path for determinism
    eligible_files.sort(key=lambda t: t[0])

    sha256 = hashlib.sha256()
    for normalized_rel, file_path in eligible_files:
        # Hash path bytes
        sha256.update(normalized_rel.encode("utf-8"))
        sha256.update(b"\x00")  # null separator
        # Hash file contents
        with open(file_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                sha256.update(chunk)
        sha256.update(b"\x00")  # null separator between files

    return sha256.hexdigest()


# ---------------------------------------------------------------------------
# Storage-key path resolution
# ---------------------------------------------------------------------------

def _resolve_artifact_path(storage_key: str, trusted_root: Path) -> Path:
    """Resolve storage_key to an absolute path under trusted_root.

    Raises:
        ModelLoadError: if storage_key is empty, contains invalid components,
            or resolves to a path outside trusted_root.
    """
    if not storage_key or not storage_key.strip():
        raise ModelLoadError(
            STATUS_ARTIFACT_PATH_REJECTED,
            "Model registry record has an empty storage key.",
        )

    # Reject obviously dangerous patterns before Path resolution
    normalized_key = storage_key.replace("\\", "/")
    for segment in normalized_key.split("/"):
        if segment in ("", ".", ".."):
            raise ModelLoadError(
                STATUS_ARTIFACT_PATH_REJECTED,
                "Model storage key contains invalid path components.",
            )

    # Resolve root (may not exist yet during tests)
    try:
        resolved_root = trusted_root.resolve()
    except (OSError, RuntimeError):
        raise ModelLoadError(
            STATUS_ARTIFACT_PATH_REJECTED,
            "Trusted artifact root could not be resolved.",
        )

    candidate = (resolved_root / normalized_key).resolve()

    # Containment check
    try:
        candidate.relative_to(resolved_root)
    except ValueError:
        raise ModelLoadError(
            STATUS_ARTIFACT_PATH_REJECTED,
            "Resolved model path is outside the trusted artifact root.",
        )

    return candidate


# ---------------------------------------------------------------------------
# Trusted model load sequence
# ---------------------------------------------------------------------------

def load_trusted_spacy_model(model_id: str, db: Session) -> tuple[Any, Any]:
    """Load a registered custom spaCy model through the full trust chain.

    Steps:
    1.  Validate model_id format.
    2.  Look up model_id in ExtractionModel registry.
    3.  Assert registry record status == READY.
    4.  Retrieve artifact_storage_key.
    5.  Resolve storage_key under MODEL_ARTIFACT_ROOT.
    6.  Assert resolved path cannot escape trusted root.
    7.  Assert artifact directory exists.
    8.  Compute deterministic SHA-256 of the artifact directory.
    9.  Compare computed checksum with registry metadata.
    10. Validate provider, model_type, spacy_version compatibility.
    11. Import spaCy (optional dependency) — fail if not installed.
    12. Call spacy.load() — only after all preceding checks pass.

    Returns:
        (nlp, registry_record) on success.

    Raises:
        ModelLoadError: with a structured status code on any failure.
            The exception message never contains filesystem paths.
    """
    from apps.backend.app.models.extraction_model import ExtractionModel

    # Step 1 — validate model_id
    validate_model_id(model_id)

    # Step 2 — registry lookup
    record = (
        db.query(ExtractionModel)
        .filter(ExtractionModel.model_id == model_id)
        .first()
    )
    if record is None:
        raise ModelLoadError(
            STATUS_MODEL_NOT_FOUND,
            f"Model '{model_id}' not found in the registry.",
        )

    # Step 3 — status check
    if record.status != STATUS_READY:
        raise ModelLoadError(
            STATUS_MODEL_NOT_READY,
            f"Model '{model_id}' has status '{record.status}' and cannot be loaded.",
        )

    # Step 4 — retrieve storage key
    storage_key = record.artifact_storage_key
    if not storage_key:
        raise ModelLoadError(
            STATUS_ARTIFACT_MISSING,
            f"Model '{model_id}' has no artifact storage key registered.",
        )

    # Step 5 & 6 — resolve and contain path
    trusted_root = Path(settings.MODEL_ARTIFACT_ROOT)
    resolved_artifact = _resolve_artifact_path(storage_key, trusted_root)

    # Step 7 — existence check
    if not resolved_artifact.exists():
        raise ModelLoadError(
            STATUS_ARTIFACT_MISSING,
            f"Model '{model_id}' artifact is missing from storage.",
        )

    # Step 8 — compute deterministic checksum
    computed_checksum = compute_directory_checksum(resolved_artifact, trusted_root)

    # Step 9 — compare checksums
    stored_checksum = record.sha256_checksum
    if not stored_checksum:
        raise ModelLoadError(
            STATUS_ARTIFACT_CHECKSUM_INVALID,
            f"Model '{model_id}' has no stored checksum — cannot verify integrity.",
        )
    if not _constant_time_compare(computed_checksum, stored_checksum):
        logger.error(
            "Checksum mismatch for model '%s'. Expected %s…, computed %s…",
            model_id,
            stored_checksum[:8],
            computed_checksum[:8],
        )
        raise ModelLoadError(
            STATUS_ARTIFACT_CHECKSUM_INVALID,
            f"Model '{model_id}' artifact checksum does not match the registry.",
        )

    # Step 10 — metadata compatibility checks
    if record.provider not in ("SPACY_CUSTOM", "SPACY_LOCAL"):
        raise ModelLoadError(
            STATUS_MODEL_INCOMPATIBLE,
            f"Model '{model_id}' provider '{record.provider}' is not compatible "
            "with SpacyNERProvider.",
        )
    if record.model_type != "spacy_ner":
        raise ModelLoadError(
            STATUS_MODEL_INCOMPATIBLE,
            f"Model '{model_id}' has model_type '{record.model_type}', expected 'spacy_ner'.",
        )

    # Step 11 — optional spaCy import
    try:
        import spacy  # type: ignore[import-untyped]
    except ImportError:
        raise ModelLoadError(
            STATUS_PROVIDER_UNAVAILABLE,
            "spaCy is not installed. Cannot load custom NER model.",
        )

    # Optionally check version compatibility
    if record.spacy_version:
        installed_major = spacy.__version__.split(".")[0]
        registered_major = record.spacy_version.split(".")[0]
        if installed_major != registered_major:
            raise ModelLoadError(
                STATUS_MODEL_INCOMPATIBLE,
                f"Model '{model_id}' was trained with spaCy major version "
                f"{registered_major} but {installed_major} is installed.",
            )

    # Step 12 — load model (path never exposed outside this function)
    try:
        nlp = spacy.load(str(resolved_artifact))
    except Exception:
        logger.exception("spacy.load failed for model '%s'", model_id)
        raise ModelLoadError(
            STATUS_FAILED,
            f"Failed to load model '{model_id}'. Check server logs for details.",
        )

    logger.info("Trusted model '%s' loaded successfully.", model_id)
    return nlp, record


def _constant_time_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to resist timing attacks."""
    import hmac
    return hmac.compare_digest(a.encode(), b.encode())
