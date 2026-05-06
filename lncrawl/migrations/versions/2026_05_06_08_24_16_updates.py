"""Updates

Revision ID: 283ec08ff9bb
Revises: c8dffc25c2a0
Create Date: 2026-05-06 08:24:16.483099
"""

from typing import Sequence, Union

import sqlmodel as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "283ec08ff9bb"
down_revision: Union[str, Sequence[str], None] = "c8dffc25c2a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Backfill any NULL tags before tightening the constraint. The model's
    # Python-side default is `[]`, so empty list is the natural backfill.
    op.execute(sa.text("UPDATE novels SET tags = '[]' WHERE tags IS NULL"))

    # batch_alter_table is required for SQLite (no native ALTER COLUMN ...
    # NOT NULL) and works fine on Postgres/MySQL. On Postgres this is
    # effectively a no-op since the initial migration already set NOT NULL.
    with op.batch_alter_table("novels") as batch_op:
        batch_op.alter_column("tags", existing_type=sa.JSON(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("novels") as batch_op:
        batch_op.alter_column("tags", existing_type=sa.JSON(), nullable=True)
