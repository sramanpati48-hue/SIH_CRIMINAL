"""Alembic migrations environment — configured for SIH 26189 models."""

import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Ensure the backend app package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from apps.backend.app.db.base import Base  # noqa: E402

# Import all models so Alembic's autogenerate can detect them
from apps.backend.app.models.user import User  # noqa: E402, F401
from apps.backend.app.models.case import Case  # noqa: E402, F401
from apps.backend.app.models.document import Document  # noqa: E402, F401
from apps.backend.app.models.entity import ExtractedEntity  # noqa: E402, F401
from apps.backend.app.models.relationship import ExtractedRelationship  # noqa: E402, F401
from apps.backend.app.models.processing_job import ProcessingJob  # noqa: E402, F401
from apps.backend.app.models.alert import Alert  # noqa: E402, F401
from apps.backend.app.models.feedback import InvestigatorFeedback  # noqa: E402, F401
from apps.backend.app.models.audit_log import AuditLog  # noqa: E402, F401
from apps.backend.app.models.case_access import CaseAccess  # noqa: E402, F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
