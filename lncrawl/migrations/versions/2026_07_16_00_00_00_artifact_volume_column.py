"""Artifact volume column

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-16 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "artifacts",
        sa.Column("volume", sa.Integer(), nullable=True),
    )
    op.create_index("ix_artifacts_volume", "artifacts", ["volume"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_artifacts_volume", table_name="artifacts")
    op.drop_column("artifacts", "volume")
