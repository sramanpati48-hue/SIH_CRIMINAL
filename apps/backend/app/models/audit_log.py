"""Audit log SQLAlchemy model."""

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Immutable audit record tracking every system and user action."""

    __tablename__ = "audit_logs"

    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # INGEST_FILE | VERIFY_RELATION | REJECT_ENTITY | CREATE_CASE | etc.
    target_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # CASE | DOCUMENT | RELATIONSHIP | ENTITY | ALERT
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_state: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON string
    new_state: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    __table_args__ = (
        Index("ix_audit_logs_target_id", "target_id"),
        Index("ix_audit_logs_target_type", "target_type"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )
