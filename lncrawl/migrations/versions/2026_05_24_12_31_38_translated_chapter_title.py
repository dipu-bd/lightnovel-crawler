"""Translated Chapter Title

Revision ID: e7379c683408
Revises: cbe442f98921
Create Date: 2026-05-24 12:31:38.473801
"""

from typing import Sequence, Union

from alembic import op
import sqlmodel as sa
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "e7379c683408"
down_revision: Union[str, Sequence[str], None] = "cbe442f98921"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # batch_alter_table is required for SQLite (no native ADD CONSTRAINT) and
    # is a no-op on Postgres/MySQL.
    with op.batch_alter_table("chapter_translations") as batch_op:
        batch_op.add_column(
            sa.Column("chapter_title", AutoString(), nullable=False, server_default=""),
        )
        batch_op.create_unique_constraint(
            batch_op.f("chapter_translations_novel_id_chapter_serial_language_key"),
            ["novel_id", "chapter_serial", "language"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("chapter_translations") as batch_op:
        batch_op.drop_constraint(
            batch_op.f("chapter_translations_novel_id_chapter_serial_language_key"),
            type_="unique",
        )
        batch_op.drop_column("chapter_title")
