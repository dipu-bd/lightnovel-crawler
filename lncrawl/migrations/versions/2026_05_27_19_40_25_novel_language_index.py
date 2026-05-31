"""Novel language index

Revision ID: 3f82035c009e
Revises: 44072b6143b9
Create Date: 2026-05-27 19:40:25.065042
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3f82035c009e"
down_revision: Union[str, Sequence[str], None] = "44072b6143b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f("ix_novels_language"), "novels", ["language"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_novels_language"), table_name="novels")
