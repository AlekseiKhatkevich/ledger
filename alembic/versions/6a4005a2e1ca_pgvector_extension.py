"""pgvector_extension

Revision ID: 6a4005a2e1ca
Revises: 94b62d944b15
Create Date: 2026-06-16 10:41:55.413763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a4005a2e1ca'
down_revision: Union[str, Sequence[str], None] = '94b62d944b15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension for vector similarity search
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP EXTENSION IF EXISTS vector')