"""Artifact Translation

Revision ID: 44072b6143b9
Revises: a7205cc84b5d
Create Date: 2026-05-27 16:07:52.633610
"""

from typing import Sequence, Union

from alembic import op
import sqlmodel as sa
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "44072b6143b9"
down_revision: Union[str, Sequence[str], None] = "a7205cc84b5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("artifacts") as batch_op:
        batch_op.add_column(sa.Column("language", AutoString(), nullable=True))
    with op.batch_alter_table("novel_translations") as batch_op:
        batch_op.drop_column("tags")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("artifacts") as batch_op:
        batch_op.drop_column("language")
    with op.batch_alter_table("novel_translations") as batch_op:
        batch_op.add_column(sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"))
