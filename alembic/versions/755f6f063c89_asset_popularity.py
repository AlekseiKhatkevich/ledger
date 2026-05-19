"""asset popularity

Revision ID: 755f6f063c89
Revises: 10ea0ce9f705
Create Date: 2026-05-19 13:31:19.264370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from logic.db_models import AssetPopularity


# revision identifiers, used by Alembic.
revision: str = '755f6f063c89'
down_revision: Union[str, Sequence[str], None] = '10ea0ce9f705'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    AssetPopularity.create(op)  # type: ignore[arg-type]
    op.execute(
        f"ALTER TABLE {AssetPopularity.__tablename__} REPLICA IDENTITY FULL"
    )


def downgrade() -> None:
    """Downgrade schema."""
    AssetPopularity.drop(op)  # type: ignore[arg-type]
