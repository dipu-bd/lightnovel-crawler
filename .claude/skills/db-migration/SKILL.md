---
name: db-migration
description: Schema changes in lncrawl — SQLModel DAO models, Alembic migration workflow (dev migrate CLI), Postgres/SQLite dialect differences, enum-sync migrations. Use when adding/changing a DAO model field or writing/reviewing a migration.
---

# Schema changes

ORM: SQLModel/SQLAlchemy. Models in `lncrawl/dao/`, migrations in
`lncrawl/migrations/versions/`. Migrations run **automatically on startup**
(`ctx.db.bootstrap()`: ensures the DB exists, backs up SQLite to `<db>.bak` before pending
migrations, upgrades to head, verifies the schema, restores the backup on failure).

## DAO model conventions

- Every table extends `BaseTable` (`dao/_base.py`): UUID string `id` PK, `created_at`/
  `updated_at` as UNIX-ms `BigInteger` (auto-touched by a `before_update` event), and a JSON
  `extra` dict. Set `table=True` + `__tablename__`; composite indexes via `__table_args__`.
- Enum columns store the **member name** (native `ENUM` types on Postgres, VARCHAR on
  SQLite). Enums live in `lncrawl/enums.py` and are re-exported from `dao/__init__.py`, which
  also maintains the `models`/`tables` lists Alembic metadata uses.
- Use `sa_type=sa.BigInteger` for large ints, `index=True` for queried fields, and a
  `server_default` when adding a NOT NULL column to an existing table.

## Recipe

1. Edit the DAO model in `lncrawl/dao/*.py`.
2. Generate a revision: `uv run python -m lncrawl dev migrate add "message"` (autogenerate by
   default; `-n/--no-auto` for a hand-written one). Files land in `migrations/versions/` with
   a timestamp filename template and are auto-formatted by a `black` post-write hook — the
   Alembic config is built in code (`services/db.py`), not `alembic.ini`.
3. Review the generated `upgrade()`/`downgrade()` — keep them symmetric
   (`add_column`+`create_index` ↔ `drop_index`+`drop_column`). House style: module docstring
   with Revision ID/Revises/Create Date, `revision`/`down_revision` constants, and a
   `dialect = op.get_context().dialect.name` guard when behavior differs per dialect.
4. **If you changed a Python enum used as a column type** (e.g. `JobType`, `OutputFormat`):
   add a Postgres enum-sync migration modeled on an existing `sync_*` revision — raw
   `op.execute` DDL for `postgresql`, no-op elsewhere. **Autogenerate will not detect this.**
5. Verify: `uv run python -m lncrawl dev migrate verify` (upgrades to head + strict schema
   check — this is also the CI gate). Local apply/rollback/status:
   `dev migrate up` / `dev migrate down` / `dev migrate status`.

## Dialect notes

- SQLite is the default (`sqlite.db` in the data dir); `DATABASE_URL` switches to
  Postgres/MySQL. `env.py` enables `render_as_batch` only on SQLite (table-rebuild for
  ALTER/DROP support) — write normal Alembic ops and let batch mode handle it.
- Session pattern in services: `with ctx.db.session() as sess:` — `expire_on_commit=False`
  and **no auto-commit**; every writer calls `sess.commit()` explicitly.
