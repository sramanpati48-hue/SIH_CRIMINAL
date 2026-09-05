"""Local NER Provider using spaCy (Optional Dependency).

Security:
- SpacyNERProvider never accepts a filesystem path argument.
- SPACY_BASELINE loads the baseline model by fixed name (no path injection).
- SPACY_CUSTOM loads from the trusted registry via model_loader.load_trusted_spacy_model().
- If loading fails, provider status is set and RuntimeError is raised on extract().
- Paths are never logged, surfaced in exceptions, or returned to callers.
"""
from __future__ import annotations

import logging
from typing import List, Optional, TYPE_CHECKING

from apps.backend.app.extraction.providers import ExtractorProvider
from apps.backend.app.extraction.schemas import (
    DocumentExtractionResult,
    ExtractedEntityCandidate,
    ExtractedRelationshipCandidate,
)
from apps.backend.app.extraction.label_mapping import map_spacy_label
from apps.backend.app.extraction.post_processing import post_process_entities, calculate_confidence
from apps.backend.app.training.model_loader import (
    ModelLoadError,
    STATUS_PROVIDER_UNAVAILABLE,
    STATUS_MODEL_NOT_FOUND,
    STATUS_ARTIFACT_MISSING,
    STATUS_ARTIFACT_CHECKSUM_INVALID,
    STATUS_ARTIFACT_PATH_REJECTED,
    STATUS_MODEL_INCOMPATIBLE,
    STATUS_MODEL_NOT_READY,
    STATUS_FAILED,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Allow-listed baseline model name — never user-supplied.
_BASELINE_MODEL = "en_core_web_sm"

# Allow-listed provider names
PROVIDER_SPACY_BASELINE = "SPACY_BASELINE"
PROVIDER_SPACY_CUSTOM = "SPACY_CUSTOM"


class SpacyNERProvider(ExtractorProvider):
    """Optional NER provider using spaCy.

    Use SpacyNERProvider.create_baseline() for the pre-installed baseline model.
    Use SpacyNERProvider.create_custom(model_id, db) for a trained custom model.

    Neither factory accepts a filesystem path.
    """

    def __init__(
        self,
        nlp: object | None,
        provider_name: str,
        model_version: str,
        load_status: str,
        load_message: str = "",
    ) -> None:
        """Internal constructor — use factory methods."""
        self._nlp = nlp
        self._provider_name = provider_name
        self._model_version = model_version
        self._load_status = load_status
        self._load_message = load_message
        self._is_available = (nlp is not None) and (load_status == "READY")

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------

    @classmethod
    def create_baseline(cls) -> "SpacyNERProvider":
        """Create a provider backed by the pre-installed baseline spaCy model.

        Never downloads anything.  Returns an unavailable provider if spaCy
        or the baseline model is missing.
        """
        try:
            import spacy  # type: ignore[import-untyped]
        except ImportError:
            return cls(
                nlp=None,
                provider_name=PROVIDER_SPACY_BASELINE,
                model_version="N/A",
                load_status=STATUS_PROVIDER_UNAVAILABLE,
                load_message="spaCy is not installed.",
            )

        try:
            nlp = spacy.load(_BASELINE_MODEL)
            return cls(
                nlp=nlp,
                provider_name=PROVIDER_SPACY_BASELINE,
                model_version=_BASELINE_MODEL,
                load_status="READY",
            )
        except OSError:
            return cls(
                nlp=None,
                provider_name=PROVIDER_SPACY_BASELINE,
                model_version=_BASELINE_MODEL,
                load_status=STATUS_ARTIFACT_MISSING,
                load_message="Baseline spaCy model not found.",
            )

    @classmethod
    def create_custom(cls, model_id: str, db: "Session") -> "SpacyNERProvider":
        """Create a provider backed by a custom trained model from the registry.

        Performs the full trusted load sequence (model_loader.load_trusted_spacy_model).
        Never accepts a path argument.  Returns an unavailable provider on failure.
        """
        from apps.backend.app.training.model_loader import load_trusted_spacy_model

        try:
            nlp, record = load_trusted_spacy_model(model_id, db)
            return cls(
                nlp=nlp,
                provider_name=PROVIDER_SPACY_CUSTOM,
                model_version=record.model_version,
                load_status="READY",
            )
        except ModelLoadError as exc:
            logger.warning(
                "Custom model load failed for model_id='%s': [%s] %s",
                model_id,
                exc.status,
                exc.safe_message,
            )
            return cls(
                nlp=None,
                provider_name=PROVIDER_SPACY_CUSTOM,
                model_version="N/A",
                load_status=exc.status,
                load_message=exc.safe_message,
            )

    # ------------------------------------------------------------------
    # ExtractorProvider interface
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def provider_version(self) -> str:
        return "1.0.0"

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def extraction_version(self) -> str:
        return "1.0.0"

    @property
    def load_status(self) -> str:
        """Structured status code for the load result."""
        return self._load_status

    def _check_availability(self) -> None:
        """Raise RuntimeError with a safe status message if unavailable."""
        if not self._is_available:
            raise RuntimeError(
                f"SpacyNERProvider ({self._provider_name}) is unavailable: "
                f"[{self._load_status}] {self._load_message}"
            )

    def extract_entities(
        self, document_id: str, document_text: str
    ) -> List[ExtractedEntityCandidate]:
        self._check_availability()
        assert self._nlp is not None

        doc = self._nlp(document_text)
        candidates: List[ExtractedEntityCandidate] = []

        import uuid

        for ent in doc.ents:
            internal_label = map_spacy_label(ent.label_)
            if not internal_label:
                continue

            confidence = calculate_confidence(ent.label_)

            candidate = ExtractedEntityCandidate(
                candidate_id=f"ent_{uuid.uuid4().hex[:8]}",
                entity_type=internal_label,
                original_value=ent.text,
                normalized_value=ent.text.upper(),
                source_document_id=document_id,
                source_text=document_text,
                start_offset=ent.start_char,
                end_offset=ent.end_char,
                confidence=confidence,
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
            )
            candidates.append(candidate)

        return post_process_entities(candidates)

    def extract_relationships(
        self,
        document_id: str,
        document_text: str,
        entities: List[ExtractedEntityCandidate],
    ) -> List[ExtractedRelationshipCandidate]:
        self._check_availability()
        # spaCy standard pipeline does not perform relation extraction natively.
        return []

    def extract(
        self, document_id: str, document_text: str
    ) -> DocumentExtractionResult:
        self._check_availability()

        entities = self.extract_entities(document_id, document_text)
        relationships = self.extract_relationships(document_id, document_text, entities)

        return DocumentExtractionResult(
            document_id=document_id,
            entities=entities,
            relationships=relationships,
            provider=self.provider_name,
            version=self.provider_version,
        )
