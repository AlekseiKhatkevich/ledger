from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f2c15e58905e'
down_revision: Union[str, Sequence[str], None] = '926c64503946'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: create Citus extension and add worker nodes."""
    # Enable autocommit for the entire upgrade, because citus_add_node()
    # cannot run inside a transaction block.
    op.execute('COMMIT')

    # Create extension (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS citus")
    #
    # # Add worker nodes to the Citus cluster (idempotent — safe to re-run)
    # op.execute("SELECT citus_add_node('citus-worker-1', 5432)")
    # op.execute("SELECT citus_add_node('citus-worker-2', 5432)")


def downgrade() -> None:
    """Downgrade schema: remove worker nodes."""
    # Disable by dropping the extension (will also drop all distributed metadata)
    op.execute('COMMIT')
    # op.execute("SELECT citus_remove_node('citus-worker-1', 5432)")
    # op.execute("SELECT citus_remove_node('citus-worker-2', 5432)")
    op.execute("DROP EXTENSION IF EXISTS citus")