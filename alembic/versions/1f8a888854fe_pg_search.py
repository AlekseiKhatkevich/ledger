"""pg_search

Revision ID: 1f8a888854fe
Revises: 1230b7cefa57
Create Date: 2026-06-10 11:25:01.952701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f8a888854fe'
down_revision: Union[str, Sequence[str], None] = '1230b7cefa57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_search")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pg_search")
