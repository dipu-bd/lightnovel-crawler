"""announcements

Revision ID: c8dffc25c2a0
Revises: 16272c44ed84
Create Date: 2026-03-30 23:56:49.553925
"""

from typing import Sequence, Union

import sqlmodel as sa
from alembic import op
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "c8dffc25c2a0"
down_revision: Union[str, Sequence[str], None] = "16272c44ed84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "announcements",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("type", AutoString(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_by", AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id", name="pk_announcements"),
    )
    op.create_index(op.f("ix_announcement_is_active"), "announcements", ["is_active"], unique=False)
    op.create_index(op.f("ix_announcement_version"), "announcements", ["version"], unique=False)
    op.create_index(
        op.f("ix_announcements_created_at"), "announcements", ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_announcements_updated_at"), "announcements", ["updated_at"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_announcements_updated_at"), table_name="announcements")
    op.drop_index(op.f("ix_announcements_created_at"), table_name="announcements")
    op.drop_index(op.f("ix_announcement_version"), table_name="announcements")
    op.drop_index(op.f("ix_announcement_is_active"), table_name="announcements")
    op.drop_table("announcements")
