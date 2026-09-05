"""Add extraction runs table

Revision ID: 4bcc147a3094
Revises: 8237cbe94283
Create Date: 2026-09-04 01:48:39.251581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bcc147a3094'
down_revision: Union[str, Sequence[str], None] = '8237cbe94283'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'extraction_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('extraction_run_id', sa.String(length=64), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('case_id', sa.String(length=36), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('provider_version', sa.String(length=50), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('extraction_version', sa.String(length=50), nullable=False),
        sa.Column('post_processing_version', sa.String(length=50), nullable=False),
        sa.Column('relationship_rule_version', sa.String(length=50), nullable=False),
        sa.Column('dataset_version', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('entity_candidate_count', sa.Integer(), nullable=False),
        sa.Column('relationship_candidate_count', sa.Integer(), nullable=False),
        sa.Column('accepted_candidate_count', sa.Integer(), nullable=False),
        sa.Column('rejected_candidate_count', sa.Integer(), nullable=False),
        sa.Column('warning_count', sa.Integer(), nullable=False),
        sa.Column('warnings', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_extraction_runs_case_id'), 'extraction_runs', ['case_id'], unique=False)
    op.create_index(op.f('ix_extraction_runs_document_id'), 'extraction_runs', ['document_id'], unique=False)
    op.create_index(op.f('ix_extraction_runs_provider'), 'extraction_runs', ['provider'], unique=False)
    op.create_index(op.f('ix_extraction_runs_status'), 'extraction_runs', ['status'], unique=False)
    op.create_index(op.f('ix_extraction_runs_extraction_run_id'), 'extraction_runs', ['extraction_run_id'], unique=True)
    # unique constraint for idempotency identity
    op.create_unique_constraint(
        'uq_extraction_run_identity',
        'extraction_runs',
        ['document_id', 'provider', 'provider_version', 'model_version', 'extraction_version', 'post_processing_version', 'relationship_rule_version']
    )
    
    op.add_column('extracted_entities', sa.Column('extraction_run_id', sa.String(length=64), nullable=True))
    op.add_column('extracted_relationships', sa.Column('extraction_run_id', sa.String(length=64), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('extracted_relationships', 'extraction_run_id')
    op.drop_column('extracted_entities', 'extraction_run_id')
    op.drop_table('extraction_runs')
