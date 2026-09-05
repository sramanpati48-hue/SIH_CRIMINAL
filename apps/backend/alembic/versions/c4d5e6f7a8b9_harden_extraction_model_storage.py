"""Harden extraction model registry: replace artifact_path with artifact_storage_key and artifact_filename.

Revision ID: c4d5e6f7a8b9
Revises: 9327cbe94283
Create Date: 2026-09-04 20:50:00.000000

Security change:
  - Removes 'artifact_path' (stored full FS paths — unsafe).
  - Adds 'artifact_storage_key' (opaque relative key under MODEL_ARTIFACT_ROOT).
  - Adds 'artifact_filename' (basename only, no path separators).
  - Existing rows with artifact_path data have the column value discarded;
    they will need to be re-registered via the training pipeline.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4d5e6f7a8b9'
down_revision = '9327cbe94283'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('extraction_models') as batch_op:
        # Remove the unsafe full-path column
        batch_op.drop_column('artifact_path')
        # Add the new opaque storage-key column
        batch_op.add_column(
            sa.Column('artifact_storage_key', sa.String(length=500), nullable=True)
        )
        # Add the artifact filename (basename only)
        batch_op.add_column(
            sa.Column('artifact_filename', sa.String(length=255), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table('extraction_models') as batch_op:
        batch_op.drop_column('artifact_filename')
        batch_op.drop_column('artifact_storage_key')
        # Restore the original column (values will be NULL after downgrade)
        batch_op.add_column(
            sa.Column('artifact_path', sa.String(length=500), nullable=True)
        )
