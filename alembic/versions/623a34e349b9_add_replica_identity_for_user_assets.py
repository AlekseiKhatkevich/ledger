"""add replica identity for asset_popularity

Revision ID: 623a34e349b9
Revises: 10ea0ce9f705
Create Date: 2026-05-19 12:12:59.900360

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '623a34e349b9'
down_revision: Union[str, Sequence[str], None] = '10ea0ce9f705'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Set REPLICA IDENTITY to FULL for asset_popularity.
    # pg_ivm creates a UNIQUE index but not a PRIMARY KEY on IMMV tables.
    # The unique index column (ticker_id) is nullable, so it cannot be used
    # as REPLICA IDENTITY (Postgres requires NOT NULL columns for index-based
    # replica identity). FULL mode uses all columns instead.
    # Logical replication (pgcache_pub) requires REPLICA IDENTITY on any table
    # that is part of a publication and gets updated via pg_ivm triggers.
    #
    # NOTE: pg_ivm officially does NOT support IMMV together with logical
    # replication (see README — "Logical replication is not supported").
    # Alternative (preferred) approach — remove asset_popularity from the
    # publication instead of setting REPLICA IDENTITY:
    #
    #   ALTER PUBLICATION pgcache_pub DROP TABLE asset_popularity;
    #
    # This avoids the need for REPLICA IDENTITY entirely, since pg_ivm
    # already maintains the IMMV on the source.
    #
    # See: https://github.com/sraoss/pg_ivm/issues/110
    op.execute(
        "ALTER TABLE asset_popularity REPLICA IDENTITY FULL"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "ALTER TABLE asset_popularity REPLICA IDENTITY DEFAULT"
    )