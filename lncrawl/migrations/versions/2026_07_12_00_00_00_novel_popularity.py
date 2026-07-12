"""Novel Popularity

Revision ID: a1b2c3d4e5f6
Revises: df3232e15be5
Create Date: 2026-07-12 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "df3232e15be5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "novels",
        sa.Column("popularity", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.create_index("ix_novels_popularity", "novels", ["popularity"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_novels_popularity", table_name="novels")
    op.drop_column("novels", "popularity")
