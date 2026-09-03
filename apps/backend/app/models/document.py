"""Document (evidence file) SQLAlchemy model."""

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Uploaded evidence document linked to a case."""

    __tablename__ = "documents"

    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # CDR | TEXT_REPORT | BANK_STATEMENT | LOCATION_LOG | VEHICLE_LOG
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UPLOADED"
    )  # UPLOADED | PROCESSING | PROCESSED | FAILED
    uploaded_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="documents")

    __table_args__ = (
        Index("ix_documents_case_id", "case_id"),
        Index("ix_documents_status", "status"),
        Index("ix_documents_file_type", "file_type"),
        Index("ix_documents_created_at", "created_at"),
    )


# Avoid circular import
from apps.backend.app.models.case import Case  # noqa: E402
