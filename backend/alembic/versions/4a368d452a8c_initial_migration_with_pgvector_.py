"""Initial migration with pgvector extension

Revision ID: 4a368d452a8c
Revises:
Create Date: 2025-12-10 11:07:57.903800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '4a368d452a8c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create inbox_items table
    op.create_table('inbox_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('processing', 'review', 'done', name='inbox_status'), nullable=True),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('ai_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create matters table
    op.create_table('matters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Enum('active', 'expired', 'terminated', name='matter_status'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create documents table
    op.create_table('documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('matter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('content_embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['matter_id'], ['matters.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('documents')
    op.drop_table('matters')
    op.drop_table('inbox_items')