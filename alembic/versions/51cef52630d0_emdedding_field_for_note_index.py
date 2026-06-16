"""emdedding field for Note index

Revision ID: 51cef52630d0
Revises: 601fd206e213
Create Date: 2026-06-16 11:13:01.093103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51cef52630d0'
down_revision: Union[str, Sequence[str], None] = '601fd206e213'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('notes_vector_idx', 'notes', ['embedding'], unique=False, postgresql_using='hnsw', postgresql_ops={'embedding': 'vector_cosine_ops'})



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('notes_vector_idx', table_name='notes', postgresql_using='hnsw', postgresql_ops={'embedding': 'vector_cosine_ops'})

