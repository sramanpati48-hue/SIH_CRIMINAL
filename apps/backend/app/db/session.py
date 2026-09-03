"""Database session and engine configuration.

Uses SQLAlchemy synchronous engine for the prototype.
The DATABASE_URL setting controls the connection target:
  - SQLite for testing (sqlite:///...)
  - PostgreSQL for deployment (postgresql+psycopg2://...)
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.backend.app.core.config import settings

# Determine connect args based on driver
_connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
