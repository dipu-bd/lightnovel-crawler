"""Update JobType

Revision ID: cbe442f98921
Revises: 50305dbf6d2a
Create Date: 2026-05-23 02:20:33.219089
"""

from typing import Sequence, Union

from alembic import op

from lncrawl.enums import JobType

# revision identifiers, used by Alembic.
revision: str = "cbe442f98921"
down_revision: Union[str, Sequence[str], None] = "50305dbf6d2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


_NEW_VALUES = {
    JobType.TRANSLATION,
    JobType.TRANSLATION_BATCH,
}


def upgrade() -> None:
    """Upgrade schema."""
    if dialect == "postgresql":
        for member in _NEW_VALUES:
            op.execute(f"ALTER TYPE jobtype ADD VALUE IF NOT EXISTS '{member.name}'")


def downgrade() -> None:
    """Downgrade schema."""
    if dialect == "postgresql":
        # PostgreSQL cannot DROP ENUM values directly; recreate the type.
        # Rows using the removed values must be deleted first.
        removed = ", ".join(f"'{m.name}'" for m in _NEW_VALUES)
        op.execute(f"DELETE FROM jobs WHERE type IN ({removed})")

        old_values = ", ".join(f"'{m.name}'" for m in JobType if m not in _NEW_VALUES)
        op.execute("ALTER TABLE jobs ALTER COLUMN type TYPE varchar USING type::varchar")
        op.execute("DROP TYPE jobtype")
        op.execute(f"CREATE TYPE jobtype AS ENUM ({old_values})")
        op.execute("ALTER TABLE jobs ALTER COLUMN type TYPE jobtype USING type::jobtype")
