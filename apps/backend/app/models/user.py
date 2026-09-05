"""User and Role SQLAlchemy models."""

import enum
from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Role(str, enum.Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    INVESTIGATOR = "INVESTIGATOR"
    ANALYST = "ANALYST"
    REVIEWER = "REVIEWER"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """System user account."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default=Role.ANALYST.value
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    __table_args__ = (
        Index("ix_users_username", "username"),
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
    )
