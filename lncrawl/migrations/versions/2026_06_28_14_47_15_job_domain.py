"""Job Domain

Revision ID: df3232e15be5
Revises: f3b0a1c2d4e5
Create Date: 2026-06-28 14:47:15.628111
"""

from typing import Sequence, Union

from alembic import op
import sqlmodel as sa
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "df3232e15be5"
down_revision: Union[str, Sequence[str], None] = "f3b0a1c2d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("jobs", sa.Column("domain", AutoString(), nullable=True))
    op.create_index("ix_jobs_domain", "jobs", ["domain"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_jobs_domain", table_name="jobs")
    op.drop_column("jobs", "domain")
