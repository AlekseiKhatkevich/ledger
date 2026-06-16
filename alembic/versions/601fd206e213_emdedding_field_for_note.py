"""emdedding field for Note

Revision ID: 601fd206e213
Revises: 6a4005a2e1ca
Create Date: 2026-06-16 11:03:49.640561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector


# revision identifiers, used by Alembic.
revision: str = '601fd206e213'
down_revision: Union[str, Sequence[str], None] = '6a4005a2e1ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('notes', sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=True))



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('notes', 'embedding')
