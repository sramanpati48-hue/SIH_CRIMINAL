"""Extracted relationship SQLAlchemy model."""

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ExtractedRelationship(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Relationship between two extracted entities, linked to source evidence."""

    __tablename__ = "extracted_relationships"

    extraction_run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    source_entity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("extracted_entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_entity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("extracted_entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    relation_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # CALL_MADE | TRANSFERRED_FUNDS | USED_ALIAS | CO_LOCATED | etc.
    source_text_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_offset: Mapped[int | None] = mapped_column(nullable=True)
    end_offset: Mapped[int | None] = mapped_column(nullable=True)
    
    event_timestamp: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    attributes: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(3, 2), nullable=True
    )
    verification_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UNREVIEWED"
    )  # UNREVIEWED | PENDING | ACCEPTED | REJECTED | CORRECTED | NEEDS_MORE_INFORMATION
    
    extraction_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extraction_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    relationship_rule_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewer_identity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    review_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    verified_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    verified_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
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
        Index("ix_extracted_relationships_case_id", "case_id"),
        Index("ix_extracted_relationships_relation_type", "relation_type"),
        Index(
            "ix_extracted_relationships_verification_status", "verification_status"
        ),
        Index("ix_extracted_relationships_source_entity_id", "source_entity_id"),
        Index("ix_extracted_relationships_target_entity_id", "target_entity_id"),
        Index("ix_extracted_rel_source", "source_record_type", "source_record_id"),
        Index("ix_extracted_rel_graph_sync", "graph_sync_status"),
    )
