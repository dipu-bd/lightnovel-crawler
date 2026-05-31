"""Sync JobType

Revision ID: a7205cc84b5d
Revises: 0d2b9d1e250c
Create Date: 2026-05-24 22:27:51.213869
"""

from typing import Sequence, Union

from alembic import op

from lncrawl.enums import JobType

# revision identifiers, used by Alembic.
revision: str = "a7205cc84b5d"
down_revision: Union[str, Sequence[str], None] = "0d2b9d1e250c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


_available_keys = frozenset([m.name for m in JobType])
_old_vs_new_keys = {
    ("TRANSLATION", "CHAPTER_TRANSLATION"),
    ("TRANSLATION_BATCH", "CHAPTER_TRANSLATION_BATCH"),
}


def _rename_old_to_new() -> None:
    for _old, _new in _old_vs_new_keys:
        if _new in _available_keys:
            op.execute(f"UPDATE jobs SET type = '{_new}' WHERE type = '{_old}'")


def _rename_new_to_old() -> None:
    for _old, _new in _old_vs_new_keys:
        if _old in _available_keys:
            op.execute(f"UPDATE jobs SET type = '{_old}' WHERE type = '{_new}'")


def upgrade() -> None:
    """Upgrade schema."""
    if dialect == "postgresql":
        names = ", ".join(f"'{m.name}'" for m in JobType)
        op.execute("ALTER TABLE jobs ALTER COLUMN type TYPE varchar USING type::varchar")
        _rename_old_to_new()
        op.execute("DROP TYPE jobtype")
        op.execute(f"CREATE TYPE jobtype AS ENUM ({names})")
        op.execute("ALTER TABLE jobs ALTER COLUMN type TYPE jobtype USING type::jobtype")
    else:
        _rename_old_to_new()


def downgrade() -> None:
    """Downgrade schema."""
    if dialect == "postgresql":
        names = ", ".join(f"'{m.name}'" for m in JobType)
        op.execute("ALTER TABLE jobs ALTER COLUMN type TYPE varchar USING type::varchar")
        _rename_new_to_old()
        op.execute("DROP TYPE jobtype")
        op.execute(f"CREATE TYPE jobtype AS ENUM ({names})")
        op.execute("ALTER TABLE jobs ALTER COLUMN type TYPE jobtype USING type::jobtype")
    else:
        _rename_new_to_old()
