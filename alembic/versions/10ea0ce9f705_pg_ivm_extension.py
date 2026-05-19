"""pg_ivm extension

Revision ID: 10ea0ce9f705
Revises: d213fe43ae09
Create Date: 2026-05-19 11:54:07.195385

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '10ea0ce9f705'
down_revision: Union[str, Sequence[str], None] = 'd213fe43ae09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_ivm")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS pg_ivm")
