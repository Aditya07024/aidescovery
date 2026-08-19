"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-19 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Entities table
    op.create_table(
        'entities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location_summary', sa.String(length=255), nullable=True),
        sa.Column('website', sa.String(length=512), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('attributes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_entities_entity_type', 'entities', ['entity_type'])
    op.create_index('ix_entities_name', 'entities', ['name'])

    # People table
    op.create_table(
        'people',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=True),
        sa.Column('given_name', sa.String(length=100), nullable=True),
        sa.Column('family_name', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('experience_years', sa.Float(), nullable=True),
        sa.Column('current_role', sa.String(length=255), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Searches table
    op.create_table(
        'searches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('raw_query', sa.Text(), nullable=False),
        sa.Column('entity_type_override', sa.String(length=50), nullable=True),
        sa.Column('structured_plan', sa.JSON(), nullable=True),
        sa.Column('selected_sources', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('discovered_count', sa.Integer(), nullable=True),
        sa.Column('qualified_count', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Search Results table
    op.create_table(
        'search_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('search_id', sa.String(length=36), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('is_qualified', sa.Boolean(), nullable=True),
        sa.Column('qualification_reasons', sa.JSON(), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['search_id'], ['searches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('key_prefix', sa.String(length=20), nullable=False),
        sa.Column('hashed_key', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('api_keys')
    op.drop_table('search_results')
    op.drop_table('searches')
    op.drop_table('people')
    op.drop_table('entities')
