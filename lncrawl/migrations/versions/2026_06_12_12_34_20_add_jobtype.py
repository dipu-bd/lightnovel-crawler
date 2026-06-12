"""Add JobType

Revision ID: 527569d17dfc
Revises: 77f5462a77e2
Create Date: 2026-06-12 12:34:20.903311
"""

from typing import Sequence, Union

from alembic import op

from lncrawl.enums import JobType

# revision identifiers, used by Alembic.
revision: str = "527569d17dfc"
down_revision: Union[str, Sequence[str], None] = "77f5462a77e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    if dialect == "postgresql":
        names = ", ".join(f"'{m.name}'" for m in JobType)
        op.execute("ALTER TABLE jobs ALTER COLUMN type TYPE varchar USING type::varchar")
        op.execute("DROP TYPE jobtype")
        op.execute(f"CREATE TYPE jobtype AS ENUM ({names})")
        op.execute("ALTER TABLE jobs ALTER COLUMN type TYPE jobtype USING type::jobtype")


def downgrade() -> None:
    """Downgrade schema."""
    upgrade()
