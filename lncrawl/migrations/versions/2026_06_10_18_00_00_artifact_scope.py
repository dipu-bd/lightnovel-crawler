"""Artifact scope

Revision ID: 22fd3f1f3558
Revises: 77f5462a77e2
Create Date: 2026-06-10 18:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlmodel as sa
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "22fd3f1f3558"
down_revision: Union[str, Sequence[str], None] = "77f5462a77e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("artifacts") as batch_op:
        batch_op.add_column(sa.Column("scope_mode", AutoString(), nullable=True))
        batch_op.add_column(sa.Column("scope_label", AutoString(), nullable=True))
        batch_op.add_column(sa.Column("start_volume_serial", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("end_volume_serial", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("start_chapter_serial", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("end_chapter_serial", sa.Integer(), nullable=True))
        batch_op.create_index("ix_artifacts_scope_mode", ["scope_mode"])
        batch_op.create_index("ix_artifacts_start_volume_serial", ["start_volume_serial"])
        batch_op.create_index("ix_artifacts_end_volume_serial", ["end_volume_serial"])
        batch_op.create_index("ix_artifacts_start_chapter_serial", ["start_chapter_serial"])
        batch_op.create_index("ix_artifacts_end_chapter_serial", ["end_chapter_serial"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("artifacts") as batch_op:
        batch_op.drop_index("ix_artifacts_end_chapter_serial")
        batch_op.drop_index("ix_artifacts_start_chapter_serial")
        batch_op.drop_index("ix_artifacts_end_volume_serial")
        batch_op.drop_index("ix_artifacts_start_volume_serial")
        batch_op.drop_index("ix_artifacts_scope_mode")
        batch_op.drop_column("end_chapter_serial")
        batch_op.drop_column("start_chapter_serial")
        batch_op.drop_column("end_volume_serial")
        batch_op.drop_column("start_volume_serial")
        batch_op.drop_column("scope_label")
        batch_op.drop_column("scope_mode")
