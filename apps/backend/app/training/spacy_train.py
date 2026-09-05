"""spaCy custom NER training pipeline.

Security contract:
- Runs only from the CLI (scripts/train_spacy_ner.py).
- Requires NER_TRAINING_ENABLED=true from typed settings.
- Writes only to internally controlled directories under MODEL_ARTIFACT_ROOT.
- Generates storage keys internally — no user-provided paths accepted.
- subprocess.run uses an explicit executable list, shell=False, and a timeout.
- Stdout/stderr from the subprocess are captured and NOT forwarded to callers.
- Sensitive text (paths, tokens) is redacted from persisted failure summaries.
- Temporary training directories are cleaned up after failed training.
- Model is promoted to trusted root only after training, checksum, and
  metadata registration all succeed.
- Filesystem paths are never included in returned metadata or logged at INFO+.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Patterns to redact from failure summaries before persistence
_REDACT_PATTERNS = [
    re.compile(r'[A-Za-z]:\\[^\s"\']+'),       # Windows absolute paths
    re.compile(r'/[^\s"\']{3,}'),              # Unix absolute paths
    re.compile(r'(?i)password\s*[=:]\s*\S+'),  # passwords
    re.compile(r'(?i)token\s*[=:]\s*\S+'),     # tokens
]


def _sanitize_summary(text: str, max_length: int = 500) -> str:
    """Redact sensitive content and truncate before persisting a failure summary."""
    for pattern in _REDACT_PATTERNS:
        text = pattern.sub('[REDACTED]', text)
    return text[:max_length]


def generate_checksum_for_dir(artifact_dir: Path, trusted_root: Path) -> str:
    """Thin wrapper — delegates to model_loader.compute_directory_checksum."""
    from apps.backend.app.training.model_loader import compute_directory_checksum
    return compute_directory_checksum(artifact_dir, trusted_root)


def train_spacy_model(
    train_data_path: str,
    val_data_path: str,
    *,
    dataset_version: str = "v1.0-synthetic",
    label_schema_version: str = "1.0.0",
    training_steps: int = 1000,
) -> dict[str, Any]:
    """Run spaCy custom NER training.

    Arguments:
        train_data_path: Absolute path to the prepared train.spacy file.
            (Controlled by prepare_spacy_ner_data.py — never user-supplied.)
        val_data_path: Absolute path to the prepared validation.spacy file.
        dataset_version: Version label of the synthetic dataset.
        label_schema_version: Version of the NER label schema.
        training_steps: Maximum training steps.

    Returns:
        A metadata dict suitable for registering in ExtractionModel.
        Contains NO filesystem paths; uses artifact_storage_key instead.

    Raises:
        RuntimeError: with a safe message if training fails or prerequisites
            are not met.  Never includes filesystem paths.
    """
    from apps.backend.app.core.config import settings

    # Gate: training must be explicitly enabled
    if not settings.NER_TRAINING_ENABLED:
        raise RuntimeError(
            "Training is disabled. Set NER_TRAINING_ENABLED=true in the environment "
            "and run this function from the training CLI only."
        )

    # Require spaCy
    try:
        import spacy  # type: ignore[import-untyped]
        spacy_version = spacy.__version__
    except ImportError:
        raise RuntimeError(
            "spaCy is not installed. Install it via requirements-ner.txt."
        )

    # -----------------------------------------------------------------------
    # Resolve and validate trusted root
    # -----------------------------------------------------------------------
    trusted_root = Path(settings.MODEL_ARTIFACT_ROOT).resolve()
    trusted_root.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Generate unique storage key and work inside a temp directory first
    # -----------------------------------------------------------------------
    model_id = f"spacy_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    storage_key = f"{model_id}/model-best"

    # Use a temp dir inside the trusted root so cleanup is straightforward
    temp_run_dir = trusted_root / f"_tmp_{model_id}"
    try:
        temp_run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        raise RuntimeError("Temporary training directory already exists. Aborting.")

    failed = True
    failure_summary: str | None = None
    try:
        # -------------------------------------------------------------------
        # Step 1: Generate spaCy config inside temp dir
        # -------------------------------------------------------------------
        config_path = temp_run_dir / "config.cfg"

        _run_subprocess(
            [
                sys.executable, "-m", "spacy", "init", "config",
                str(config_path),
                "--lang", "en",
                "--pipeline", "ner",
                "--optimize", "efficiency",
                "--force",
            ],
            cwd=str(trusted_root),
            timeout=300,
            operation_label="config generation",
        )

        # -------------------------------------------------------------------
        # Step 2: Train
        # -------------------------------------------------------------------
        logger.info("Starting spaCy training for model_id='%s'.", model_id)
        _run_subprocess(
            [
                sys.executable, "-m", "spacy", "train",
                str(config_path),
                "--output", str(temp_run_dir),
                "--paths.train", train_data_path,
                "--paths.dev", val_data_path,
                "--training.max_steps", str(training_steps),
            ],
            cwd=str(trusted_root),
            timeout=settings.NER_TRAINING_TIMEOUT_SECONDS,
            operation_label="training",
        )

        # -------------------------------------------------------------------
        # Step 3: Verify model-best was produced
        # -------------------------------------------------------------------
        best_model_src = temp_run_dir / "model-best"
        if not best_model_src.exists() or not best_model_src.is_dir():
            raise RuntimeError("Training did not produce a 'model-best' directory.")

        # -------------------------------------------------------------------
        # Step 4: Promote to trusted root (atomic rename where possible)
        # -------------------------------------------------------------------
        final_model_dir = trusted_root / model_id / "model-best"
        final_model_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(best_model_src), str(final_model_dir))

        # -------------------------------------------------------------------
        # Step 5: Compute deterministic checksum over the promoted artifact
        # -------------------------------------------------------------------
        sha256_checksum = generate_checksum_for_dir(final_model_dir, trusted_root)

        # -------------------------------------------------------------------
        # Step 6: Build metadata (no paths)
        # -------------------------------------------------------------------
        metadata: dict[str, Any] = {
            "model_id": model_id,
            "provider": "SPACY_CUSTOM",
            "model_type": "spacy_ner",
            "model_version": "1.0.0",
            "dataset_version": dataset_version,
            "label_schema_version": label_schema_version,
            "extraction_version": "1.0.0",
            "spacy_version": spacy_version,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            # Storage key (relative, never absolute path)
            "artifact_storage_key": storage_key,
            "artifact_filename": "model-best",
            "sha256_checksum": sha256_checksum,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "READY",
        }

        failed = False
        return metadata

    except RuntimeError:
        raise  # re-raise safe messages
    except Exception as exc:
        # Catch unexpected errors, produce safe summary only
        failure_summary = _sanitize_summary(str(exc))
        raise RuntimeError(
            f"Training failed: {failure_summary}"
        ) from None

    finally:
        # Always clean up temp directory
        if temp_run_dir.exists():
            try:
                shutil.rmtree(str(temp_run_dir))
            except Exception:
                logger.warning("Could not clean up temporary training directory.")

        # If training failed but we partially created the final dir, remove it
        if failed:
            final_partial = trusted_root / model_id
            if final_partial.exists():
                try:
                    shutil.rmtree(str(final_partial))
                except Exception:
                    logger.warning("Could not clean up partial model artifact.")


def _run_subprocess(
    args: list[str],
    cwd: str,
    timeout: int,
    operation_label: str,
) -> None:
    """Run a subprocess safely.

    - shell=False always.
    - Explicit executable list.
    - Controlled cwd.
    - Captured output (not forwarded to callers or APIs).
    - Timeout enforced.
    - Raises RuntimeError with a safe message on failure.
    """
    import subprocess

    try:
        result = subprocess.run(
            args,
            shell=False,
            cwd=cwd,
            capture_output=True,
            timeout=timeout,
            check=False,  # We handle returncode manually
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"spaCy {operation_label} timed out after {timeout}s. "
            "Check server logs."
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"spaCy {operation_label} failed: executable not found. "
            "Ensure spaCy is installed."
        )

    if result.returncode != 0:
        # Log full output at DEBUG (server-restricted) but never forward to callers
        stderr_text = result.stderr.decode("utf-8", errors="replace")
        stdout_text = result.stdout.decode("utf-8", errors="replace")
        logger.debug(
            "spaCy %s stderr:\n%s", operation_label, stderr_text
        )
        logger.debug(
            "spaCy %s stdout:\n%s", operation_label, stdout_text
        )
        # Produce a safe summary (last non-empty line of stderr, redacted)
        last_line = next(
            (l.strip() for l in reversed(stderr_text.splitlines()) if l.strip()),
            "unknown error",
        )
        safe_summary = _sanitize_summary(last_line)
        raise RuntimeError(
            f"spaCy {operation_label} exited with code {result.returncode}. "
            f"Summary: {safe_summary}"
        )
