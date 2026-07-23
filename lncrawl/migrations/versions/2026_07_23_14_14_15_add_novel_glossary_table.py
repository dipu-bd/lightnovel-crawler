"""Add novel glossary table

Revision ID: 064c024aa744
Revises: e5f6a7b8c9d0
Create Date: 2026-07-23 14:14:15.757660
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "064c024aa744"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "novel_glossaries",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("language", AutoString(), nullable=False),
        sa.Column("terms", sa.JSON(), nullable=False, server_default="{}"),
        sa.PrimaryKeyConstraint("id", name=op.f("novel_glossaries_pkey")),
        sa.ForeignKeyConstraint(
            ["novel_id"],
            ["novels.id"],
            ondelete="CASCADE",
            name="novel_glossaries_novel_id_fkey",
        ),
        sa.UniqueConstraint("novel_id", "language", name="novel_glossaries_novel_id_language_key"),
    )
    op.create_index(
        "ix_novel_glossary_lookup",
        "novel_glossaries",
        ["novel_id", "language"],
        unique=False,
    )
    op.create_index(
        op.f("ix_novel_glossaries_created_at"),
        "novel_glossaries",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_novel_glossaries_updated_at"),
        "novel_glossaries",
        ["updated_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    if dialect != "sqlite":
        op.drop_constraint(
            op.f("novel_glossaries_novel_id_fkey"),
            "novel_glossaries",
            type_="foreignkey",
        )

    op.drop_index(op.f("ix_novel_glossaries_updated_at"), table_name="novel_glossaries")
    op.drop_index(op.f("ix_novel_glossaries_created_at"), table_name="novel_glossaries")
    op.drop_index("ix_novel_glossary_lookup", table_name="novel_glossaries")
    op.drop_table("novel_glossaries")
