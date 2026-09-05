"""Case Access control SQLAlchemy model."""

import enum
from datetime import datetime
from sqlalchemy import ForeignKey, Index, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CaseAccessLevel(str, enum.Enum):
    VIEW = "VIEW"
    ANALYZE = "ANALYZE"
    REVIEW = "REVIEW"
    MANAGE = "MANAGE"

    @classmethod
    def hierarchy(cls):
        return {
            cls.MANAGE: [cls.MANAGE, cls.REVIEW, cls.ANALYZE, cls.VIEW],
            cls.REVIEW: [cls.REVIEW, cls.ANALYZE, cls.VIEW],
            cls.ANALYZE: [cls.ANALYZE, cls.VIEW],
            cls.VIEW: [cls.VIEW],
        }
    
    def includes(self, required_level: "CaseAccessLevel") -> bool:
        return required_level in self.hierarchy()[self]


class CaseAccess(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Assignment mapping a user to a case with a specific access level."""

    __tablename__ = "case_access"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id"), nullable=False)
    access_level: Mapped[str] = mapped_column(String(50), nullable=False)
    
    assigned_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    case = relationship("Case", foreign_keys=[case_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_user_id])

    __table_args__ = (
        Index("ix_case_access_user_id", "user_id"),
        Index("ix_case_access_case_id", "case_id"),
        Index("ix_case_access_is_active", "is_active"),
        # We can't enforce a unique constraint on (user_id, case_id) easily because 
        # a user might have historical revoked records. We could do a unique partial index,
        # but SQLAlchemy core doesn't support partial index directly in standard __table_args__ easily for all backends.
    )
