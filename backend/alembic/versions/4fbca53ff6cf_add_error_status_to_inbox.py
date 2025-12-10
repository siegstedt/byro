"""add_error_status_to_inbox

Revision ID: 4fbca53ff6cf
Revises: 4a368d452a8c
Create Date: 2025-12-10 11:22:42.162558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fbca53ff6cf'
down_revision: Union[str, Sequence[str], None] = '4a368d452a8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add 'error' status to inbox_status enum
    op.execute("ALTER TYPE inbox_status ADD VALUE 'error'")


def downgrade() -> None:
    """Downgrade schema."""
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum without the 'error' value
    # For simplicity, we'll leave the enum as-is for downgrade
    pass
