"""add relationship_rule_version

Revision ID: 8237cbe94283
Revises: 5fc125e5f8d3
Create Date: 2026-09-03 14:06:31.090246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8237cbe94283'
down_revision: Union[str, Sequence[str], None] = '5fc125e5f8d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('extracted_relationships', sa.Column('relationship_rule_version', sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('extracted_relationships', 'relationship_rule_version')
