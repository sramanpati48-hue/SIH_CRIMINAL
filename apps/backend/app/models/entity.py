"""Extracted entity SQLAlchemy model."""

from sqlalchemy import ForeignKey, Index, Numeric, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ExtractedEntity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Entity extracted from evidence documents."""

    __tablename__ = "extracted_entities"

    extraction_run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    original_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False) # serves as normalized_value
    
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_offset: Mapped[int | None] = mapped_column(nullable=True)
    end_offset: Mapped[int | None] = mapped_column(nullable=True)
    
    attributes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON string for extra attributes
    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(3, 2), nullable=True
    )
    verification_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UNREVIEWED"
    )  # UNREVIEWED | PENDING | ACCEPTED | REJECTED | CORRECTED | NEEDS_MORE_INFORMATION
    extraction_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extraction_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewer_identity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    review_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_record_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_record_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    graph_sync_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING"
    )  # PENDING | SYNCED | RETRYABLE_FAILURE | PERMANENT_FAILURE | NOT_APPLICABLE
    graph_sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    graph_synced_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_extracted_entities_case_id", "case_id"),
        Index("ix_extracted_entities_entity_type", "entity_type"),
        Index("ix_extracted_entities_verification_status", "verification_status"),
        Index("ix_extracted_entities_source", "source_record_type", "source_record_id"),
        Index("ix_extracted_entities_graph_sync", "graph_sync_status"),
    )
