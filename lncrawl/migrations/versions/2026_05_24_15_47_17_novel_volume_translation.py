"""Novel/Volume Translation

Revision ID: 0d2b9d1e250c
Revises: e7379c683408
Create Date: 2026-05-24 15:47:17.803688
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlmodel as sa
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "0d2b9d1e250c"
down_revision: Union[str, Sequence[str], None] = "e7379c683408"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    # NovelTranslation table
    op.create_table(
        "novel_translations",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("language", AutoString(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("authors", AutoString(), nullable=True),
        sa.Column("synopsis", AutoString(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
        sa.PrimaryKeyConstraint("id", name=op.f("novel_translations_pkey")),
        sa.ForeignKeyConstraint(
            ["novel_id"],
            ["novels.id"],
            ondelete="CASCADE",
            name="novel_translations_novel_id_fkey",
        ),
        sa.UniqueConstraint(
            "novel_id", "language", name="novel_translations_novel_id_language_key"
        ),
    )
    op.create_index(
        "ix_novel_translation_lookup",
        "novel_translations",
        ["novel_id", "language"],
        unique=False,
    )
    op.create_index(
        op.f("ix_novel_translations_created_at"),
        "novel_translations",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_novel_translations_updated_at"),
        "novel_translations",
        ["updated_at"],
        unique=False,
    )
    if dialect == "postgresql":
        op.alter_column(
            "novels", "tags", existing_type=postgresql.JSON(astext_type=sa.Text()), nullable=False
        )

    # VolumeTranslation table
    op.create_table(
        "volume_translations",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("volume_serial", sa.Integer(), nullable=False),
        sa.Column("language", AutoString(), nullable=False),
        sa.Column("volume_title", AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("volume_translations_pkey")),
        sa.ForeignKeyConstraint(
            ["novel_id"],
            ["novels.id"],
            ondelete="CASCADE",
            name="volume_translations_novel_id_fkey",
        ),
        sa.UniqueConstraint(
            "novel_id",
            "volume_serial",
            "language",
            name="volume_translations_novel_id_volume_serial_language_key",
        ),
    )
    op.create_index(
        op.f("ix_volume_translation_lookup"),
        "volume_translations",
        ["novel_id", "volume_serial", "language"],
        unique=False,
    )
    op.create_index(
        op.f("ix_volume_translations_created_at"),
        "volume_translations",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_volume_translations_updated_at"),
        "volume_translations",
        ["updated_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    if dialect != "sqlite":
        op.drop_constraint(
            op.f("novel_translations_novel_id_fkey"),
            "novel_translations",
            type_="foreignkey",
        )
        op.drop_constraint(
            op.f("volume_translations_novel_id_fkey"),
            "volume_translations",
            type_="foreignkey",
        )

    op.drop_index(op.f("ix_volume_translations_updated_at"), table_name="volume_translations")
    op.drop_index(op.f("ix_volume_translations_created_at"), table_name="volume_translations")
    op.drop_index("ix_volume_translation_lookup", table_name="volume_translations")
    op.drop_table("volume_translations")

    op.drop_index(op.f("ix_novel_translations_updated_at"), table_name="novel_translations")
    op.drop_index(op.f("ix_novel_translations_created_at"), table_name="novel_translations")
    op.drop_index(op.f("ix_novel_translation_lookup"), table_name="novel_translations")
    op.drop_table("novel_translations")
