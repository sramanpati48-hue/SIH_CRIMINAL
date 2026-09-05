"""Add case access model

Revision ID: 59b4155ca897
Revises: c4d5e6f7a8b9
Create Date: 2026-09-04 21:56:17.119291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
"""Add case access model

Revision ID: 59b4155ca897
Revises: c4d5e6f7a8b9
Create Date: 2026-09-04 21:56:17.119291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59b4155ca897'
down_revision: Union[str, Sequence[str], None] = 'c4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('case_access',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('case_id', sa.String(length=36), nullable=False),
    sa.Column('access_level', sa.String(length=50), nullable=False),
    sa.Column('assigned_by_user_id', sa.String(length=36), nullable=True),
    sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['assigned_by_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_case_access_case_id', 'case_access', ['case_id'], unique=False)
    op.create_index('ix_case_access_is_active', 'case_access', ['is_active'], unique=False)
    op.create_index('ix_case_access_user_id', 'case_access', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_case_access_user_id', table_name='case_access')
    op.drop_index('ix_case_access_is_active', table_name='case_access')
    op.drop_index('ix_case_access_case_id', table_name='case_access')
    op.drop_table('case_access')
