"""Chapter Translations

Revision ID: 50305dbf6d2a
Revises: 283ec08ff9bb
Create Date: 2026-05-22 18:03:24.420111
"""

from typing import Sequence, Union

from alembic import op
import sqlmodel as sa
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "50305dbf6d2a"
down_revision: Union[str, Sequence[str], None] = "283ec08ff9bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "chapter_translations",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("chapter_serial", sa.Integer(), nullable=False),
        sa.Column("language", AutoString(), nullable=False),
        sa.Column("content_hash", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["novel_id"], ["novels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_chapter_translations"),
    )
    op.create_index(
        "ix_chapter_translation_lookup",
        "chapter_translations",
        ["novel_id", "chapter_serial", "language"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chapter_translations_created_at"),
        "chapter_translations",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chapter_translations_updated_at"),
        "chapter_translations",
        ["updated_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_chapter_translations_updated_at"), table_name="chapter_translations")
    op.drop_index(op.f("ix_chapter_translations_created_at"), table_name="chapter_translations")
    op.drop_index("ix_chapter_translation_lookup", table_name="chapter_translations")
    op.drop_table("chapter_translations")
