"""Annoucement Interactions

Revision ID: 7829b4c7dafb
Revises: 3f82035c009e
Create Date: 2026-05-28 15:40:00.948656
"""

from typing import Sequence, Union

from alembic import op
import sqlmodel as sa

# revision identifiers, used by Alembic.
revision: str = "7829b4c7dafb"
down_revision: Union[str, Sequence[str], None] = "3f82035c009e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("announcements") as batch_op:
        batch_op.add_column(
            sa.Column("click_count", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("close_count", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("announcements") as batch_op:
        batch_op.drop_column("close_count")
        batch_op.drop_column("click_count")
