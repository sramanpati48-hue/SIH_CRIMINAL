"""Case SQLAlchemy model."""

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Case(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Investigation case record."""

    __tablename__ = "cases"

    case_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ACTIVE"
    )  # ACTIVE | CLOSED | ARCHIVED
    priority: Mapped[str] = mapped_column(
        String(50), nullable=False, default="MEDIUM"
    )  # LOW | MEDIUM | HIGH | CRITICAL
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="case", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_cases_case_number", "case_number"),
        Index("ix_cases_status", "status"),
        Index("ix_cases_created_at", "created_at"),
        Index("ix_cases_created_by", "created_by"),
    )


# Import here to avoid circular import at module-load time
from apps.backend.app.models.document import Document  # noqa: E402
