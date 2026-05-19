"""Create asset_popularity IMMV

Revision ID: e93f5a2c1b4d
Revises: 0b3fbc6c2df7
Create Date: 2026-05-19 16:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from logic.db_models import AssetPopularity

# revision identifiers, used by Alembic.
revision: str = "e93f5a2c1b4d"
down_revision: Union[str, Sequence[str], None] = "623a34e349b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    AssetPopularity.create(op)  # type: ignore[arg-type]


def downgrade() -> None:
    """Downgrade schema."""
    AssetPopularity.drop(op)  # type: ignore[arg-type]
