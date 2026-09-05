"""Extraction Model Registry SQLAlchemy model."""
from sqlalchemy import Index, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ExtractionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Metadata registry for locally trained NER models (e.g. custom spaCy).

    Security constraints:
    - artifact_storage_key is an opaque relative key resolved against
      MODEL_ARTIFACT_ROOT at load time.  It must never contain '..' or
      absolute path components.
    - artifact_filename is the basename of the root artifact item (no path
      separators).
    - Neither field is exposed in API responses.
    - Full filesystem paths are never stored.
    """

    __tablename__ = "extraction_models"

    model_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(100), nullable=False)
    extraction_version: Mapped[str] = mapped_column(String(50), nullable=False)
    label_schema_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Opaque storage key relative to MODEL_ARTIFACT_ROOT, e.g.
    # "spacy_20260904_abc123/model-best".  No absolute paths allowed.
    artifact_storage_key: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    # Basename of the top-level artifact item (directory or file name).
    # No path separators allowed.
    artifact_filename: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    sha256_checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)

    python_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    spacy_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    training_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    train_document_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    validation_document_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    test_document_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)

    label_distribution: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    training_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    test_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Lifecycle: TRAINING → READY | FAILED → REJECTED | ARCHIVED
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="TRAINING"
    )

    __table_args__ = (
        Index("ix_extraction_models_provider", "provider"),
        Index("ix_extraction_models_status", "status"),
    )
