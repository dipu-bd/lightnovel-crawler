"""Novel Tags association

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-12 01:00:00.000000
"""

import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "novel_tags",
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("tag_name", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["novel_id"], ["novels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("novel_id", "tag_name"),
    )
    op.create_index("ix_novel_tag_name", "novel_tags", ["tag_name"], unique=False)

    # Backfill associations from the existing Novel.tags JSON column.
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, tags FROM novels")).fetchall()
    params = []
    for novel_id, tags in rows:
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except (ValueError, TypeError):
                tags = []
        seen = set()
        for tag in tags or []:
            name = (tag or "").strip()
            if name and name not in seen:
                seen.add(name)
                params.append({"novel_id": novel_id, "tag_name": name})

    if params:
        conn.execute(
            sa.text("INSERT INTO novel_tags (novel_id, tag_name) VALUES (:novel_id, :tag_name)"),
            params,
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_novel_tag_name", table_name="novel_tags")
    op.drop_table("novel_tags")
