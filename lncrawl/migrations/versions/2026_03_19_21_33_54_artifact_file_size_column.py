"""Artifact file size column

Revision ID: 16272c44ed84
Revises: 0d1f6e13db1a
Create Date: 2026-03-19 21:33:54.189838
"""

from typing import Sequence, Tuple, Union

import sqlmodel as sa
from alembic import op

from lncrawl.context import ctx
from lncrawl.core import TaskManager
from lncrawl.dao.artifact import Artifact

# revision identifiers, used by Alembic.
revision: str = "16272c44ed84"
down_revision: Union[str, Sequence[str], None] = "0d1f6e13db1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "artifacts",
        sa.Column("file_size", sa.BigInteger(), server_default=sa.literal(0), nullable=False),
    )

    conn = op.get_bind()
    executor = TaskManager(15)

    def get_size(artifact: Artifact) -> Tuple[str, int]:
        file = ctx.files.resolve(artifact.output_file)
        file_size = file.stat().st_size if file.is_file() else 0
        return (artifact.id, file_size)

    tasks = [
        executor.submit_task(
            get_size,
            Artifact(
                id=row[0],
                novel_id=row[1],
                job_id=row[2],
                user_id=row[3],
                format=row[4],
                file_name=row[5],
            ),
        )
        for row in conn.execute(
            sa.text("""
                SELECT id, novel_id, job_id, user_id, format, file_name
                FROM artifacts
            """)
        ).all()
    ]
    if not tasks:
        return

    ctx.logger.info(f"Migrating {len(tasks)} artifacts")
    results = executor.resolve_futures(tasks, fail_fast=True, unit="file")

    conn.execute(
        sa.text("UPDATE artifacts SET file_size = :file_size WHERE id = :id"),
        [{"id": item[0], "file_size": item[1]} for item in results if item is not None],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("artifacts", "file_size")
