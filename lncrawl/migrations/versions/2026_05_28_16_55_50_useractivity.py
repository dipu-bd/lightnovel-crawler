"""UserActivity

Revision ID: 57a9c4aeb183
Revises: 7829b4c7dafb
Create Date: 2026-05-28 16:55:50.937316
"""

from typing import Sequence, Union

from alembic import op
import sqlmodel as sa
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "57a9c4aeb183"
down_revision: Union[str, Sequence[str], None] = "7829b4c7dafb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_activities",
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("activity_type", sa.SmallInteger(), nullable=False),
        sa.Column("target_id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("visit_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("user_activities_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "activity_type", "target_id", name=op.f("user_activities_pkey")
        ),
    )
    op.create_index(
        op.f("ix_user_activity_target"),
        "user_activities",
        ["target_id", "activity_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_activity_user_last"),
        "user_activities",
        ["user_id", "updated_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_user_activity_target", table_name="user_activities")
    op.drop_index("ix_user_activity_user_last", table_name="user_activities")
    op.drop_table("user_activities")
