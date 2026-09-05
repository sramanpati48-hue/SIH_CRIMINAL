"""Extraction Run SQLAlchemy model."""

from sqlalchemy import DateTime, ForeignKey, Index, String, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ExtractionRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tracks versioned, idempotent extraction runs per document and provider."""

    __tablename__ = "extraction_runs"

    extraction_run_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    
    # Run Identity (Determinism)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    extraction_version: Mapped[str] = mapped_column(String(50), nullable=False)
    post_processing_version: Mapped[str] = mapped_column(String(50), nullable=False)
    relationship_rule_version: Mapped[str] = mapped_column(String(50), nullable=False)
    dataset_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING"
    )  # PENDING | RUNNING | COMPLETED | COMPLETED_WITH_WARNINGS | PROVIDER_UNAVAILABLE | FAILED
    
    # Metrics
    entity_candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    relationship_candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accepted_candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    warnings: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON where compatible
    
    started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_extraction_runs_document_id", "document_id"),
        Index("ix_extraction_runs_case_id", "case_id"),
        Index("ix_extraction_runs_provider", "provider"),
        Index("ix_extraction_runs_status", "status"),
        UniqueConstraint(
            "document_id",
            "provider",
            "provider_version",
            "model_version",
            "extraction_version",
            "post_processing_version",
            "relationship_rule_version",
            name="uq_extraction_run_identity"
        ),
    )
