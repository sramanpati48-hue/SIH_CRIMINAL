"""Processing job SQLAlchemy model."""

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProcessingJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tracks asynchronous processing tasks (NLP extraction, graph sync)."""

    __tablename__ = "processing_jobs"

    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    job_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # NLP_EXTRACTION | GRAPH_SYNC | PATTERN_DETECTION
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING"
    )  # PENDING | RUNNING | COMPLETED | COMPLETED_WITH_ERRORS | FAILED
    total_rows: Mapped[int] = mapped_column(nullable=False, default=0)
    processed_rows: Mapped[int] = mapped_column(nullable=False, default=0)
    rejected_rows: Mapped[int] = mapped_column(nullable=False, default=0)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_processing_jobs_case_id", "case_id"),
        Index("ix_processing_jobs_status", "status"),
        Index("ix_processing_jobs_created_at", "created_at"),
    )
