"""Drop native enums

Store enum columns as plain scalars instead of native database ENUM types:
IntEnum-backed columns become SMALLINT (member value); string-enum columns
(role, format) become VARCHAR keeping the member name. This removes the
Postgres ENUM types and the need for enum-sync migrations going forward.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-14 00:00:00.000000
"""

from enum import Enum
from typing import Sequence, Type, Union

from alembic import op
import sqlalchemy as sa

from lncrawl.enums import JobPriority, JobStatus, JobType, OutputFormat, UserRole, UserTier

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""

# IntEnum columns: (table, column, enum, pg-type-name)
INT_COLUMNS = [
    ("users", "tier", UserTier, "usertier"),
    ("jobs", "type", JobType, "jobtype"),
    ("jobs", "status", JobStatus, "jobstatus"),
    ("jobs", "priority", JobPriority, "jobpriority"),
]
# String-enum columns keep the member name; only the native type is dropped.
STR_COLUMNS = [
    ("users", "role", UserRole, "userrole"),
    ("artifacts", "format", OutputFormat, "outputformat"),
]


def _case(column: str, pairs: str) -> str:
    return f"(CASE {column}::text {pairs} END)"


def upgrade() -> None:
    """Upgrade schema."""
    if dialect == "postgresql":
        for table, column, enum, type_name in INT_COLUMNS:
            pairs = " ".join(f"WHEN '{m.name}' THEN {int(m.value)}" for m in enum)
            op.execute(
                f"ALTER TABLE {table} ALTER COLUMN {column} "
                f"TYPE smallint USING {_case(column, pairs)}"
            )
            op.execute(f"DROP TYPE IF EXISTS {type_name}")
        for table, column, _enum, type_name in STR_COLUMNS:
            op.execute(
                f"ALTER TABLE {table} ALTER COLUMN {column} TYPE varchar USING {column}::text"
            )
            op.execute(f"DROP TYPE IF EXISTS {type_name}")
    else:
        # SQLite/MySQL: convert names to values while the column is still a
        # string, then narrow the type. On a fresh CI database there are no
        # rows, so the UPDATEs are no-ops and only the type change applies.
        _convert(to_value=True)
        for table in {t for t, *_ in INT_COLUMNS}:
            with op.batch_alter_table(table) as batch:
                for t, column, _enum, _name in INT_COLUMNS:
                    if t == table:
                        batch.alter_column(column, type_=sa.SmallInteger())


def downgrade() -> None:
    """Downgrade schema."""
    if dialect == "postgresql":
        for table, column, enum, type_name in INT_COLUMNS:
            labels = ", ".join(f"'{m.name}'" for m in enum)
            pairs = " ".join(f"WHEN {int(m.value)} THEN '{m.name}'" for m in enum)
            op.execute(f"CREATE TYPE {type_name} AS ENUM ({labels})")
            op.execute(
                f"ALTER TABLE {table} ALTER COLUMN {column} TYPE {type_name} "
                f"USING (CASE {column} {pairs} END)::{type_name}"
            )
        for table, column, enum, type_name in STR_COLUMNS:
            labels = ", ".join(f"'{m.name}'" for m in enum)
            op.execute(f"CREATE TYPE {type_name} AS ENUM ({labels})")
            op.execute(
                f"ALTER TABLE {table} ALTER COLUMN {column} "
                f"TYPE {type_name} USING {column}::{type_name}"
            )
    else:
        for table in {t for t, *_ in INT_COLUMNS}:
            with op.batch_alter_table(table) as batch:
                for t, column, _enum, _name in INT_COLUMNS:
                    if t == table:
                        batch.alter_column(column, type_=sa.String())
        _convert(to_value=False)


def _convert(to_value: bool) -> None:
    """Rewrite IntEnum columns between member name and integer value in place."""
    enum: Type[Enum]
    for table, column, enum, _name in INT_COLUMNS:
        for member in enum:
            if to_value:
                src, dst = f"'{member.name}'", str(int(member.value))
            else:
                src, dst = str(int(member.value)), f"'{member.name}'"
            op.execute(f"UPDATE {table} SET {column} = {dst} WHERE {column} = {src}")
