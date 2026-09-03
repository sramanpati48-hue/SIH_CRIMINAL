"""Investigator feedback SQLAlchemy model."""

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class InvestigatorFeedback(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Human investigator feedback on extracted relationships or entities."""

    __tablename__ = "investigator_feedback"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # RELATIONSHIP | ENTITY | ALERT
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ACCEPT | REJECT | CORRECT
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    correction_data: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON string for corrections

    __table_args__ = (
        Index("ix_investigator_feedback_target_id", "target_id"),
        Index("ix_investigator_feedback_user_id", "user_id"),
        Index("ix_investigator_feedback_action", "action"),
    )
