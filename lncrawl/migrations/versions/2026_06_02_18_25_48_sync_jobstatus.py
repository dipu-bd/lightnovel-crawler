"""Sync JobStatus

Revision ID: 77f5462a77e2
Revises: 57a9c4aeb183
Create Date: 2026-06-02 18:25:48.502661
"""

from typing import Sequence, Union

from alembic import op

from lncrawl.enums import JobStatus

# revision identifiers, used by Alembic.
revision: str = "77f5462a77e2"
down_revision: Union[str, Sequence[str], None] = "57a9c4aeb183"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    if dialect == "postgresql":
        names = ", ".join(f"'{m.name}'" for m in JobStatus)
        op.execute("ALTER TABLE jobs ALTER COLUMN status TYPE varchar USING status::varchar")
        op.execute("DROP TYPE jobstatus")
        op.execute(f"CREATE TYPE jobstatus AS ENUM ({names})")
        op.execute("ALTER TABLE jobs ALTER COLUMN status TYPE jobstatus USING status::jobstatus")


def downgrade() -> None:
    """Downgrade schema."""
    upgrade()
