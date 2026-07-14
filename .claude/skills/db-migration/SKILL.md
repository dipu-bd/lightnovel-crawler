---
name: db-migration
description: Schema changes in lncrawl — SQLModel DAO models, Alembic migration workflow (dev migrate CLI), Postgres/SQLite dialect differences, enum-sync migrations. Use when adding/changing a DAO model field or writing/reviewing a migration.
---

# Schema changes

ORM: SQLModel/SQLAlchemy. Models in `lncrawl/dao/`, migrations in
`lncrawl/migrations/versions/`. `ctx.db.bootstrap()` runs on startup and **evolves the schema
differently per dialect** (`services/db.py`):

- **Fresh DB (any dialect):** built directly from the models with `create_all()` + `stamp head`
  — the migration history is never replayed on a new install.
- **Existing SQLite (single-user CLI/desktop):** **migration scripts are never executed at
  runtime.** A fingerprint of the models is cached in `PRAGMA user_version`; a matching
  fingerprint makes startup a single PRAGMA read (no Alembic import). On a mismatch the schema
  is reconciled *additively* — create missing tables/columns/indexes, skip drops and type
  changes — so an older app runs safely against a newer DB and no migration can corrupt data.
- **Existing Postgres/MySQL (server):** real Alembic migrations (`upgrade head`); never
  auto-downgrades when the DB is ahead of the code.

**Migration scripts still matter** — they are the mechanism for the server and the correctness
gate in CI (`dev migrate verify` replays every script from base and strict-checks against the
models). SQLite just doesn't consume them at runtime. Always generate a script for a model
change; CI fails otherwise.

**Additive-first discipline (what keeps SQLite self-healing):** prefer backward-compatible
model changes — new columns must be **nullable or have a `server_default`** (SQLite adds them
NULLable regardless). Renames, type narrowing, splits, and backfills are *non-additive*: they
apply on the server via the script, but on SQLite degrade to additive (the old column lingers,
data is not migrated). For a genuinely destructive change on the single-user path, use
`dev migrate rebuild`: it drops and recreates every table from the models and copies rows back
at the raw driver level (keeping only columns that still exist, preserving JSON `extra`
verbatim), backing up and restoring on failure. SQLite only; the server uses migration scripts.

## DAO model conventions

- Every table extends `BaseTable` (`dao/_base.py`): UUID string `id` PK, `created_at`/
  `updated_at` as UNIX-ms `BigInteger` (auto-touched by a `before_update` event), and a JSON
  `extra` dict. Set `table=True` + `__tablename__`; composite indexes via `__table_args__`.
- Enum columns are stored as **plain scalars, never native DB enums**. IntEnum columns use
  `sa_type=IntEnumType(SomeEnum)` (`dao/_enum.py`) → `SMALLINT` holding the member **value**
  (correct numeric ordering on every dialect; reads return the enum member and tolerate legacy
  name strings). String-enum columns use `sa_type=sa.Enum(SomeEnum, native_enum=False)` →
  `VARCHAR` holding the member **name**. Because there is no native `ENUM` type, adding an enum
  member needs **no migration at all** — no more `sync_*` revisions. Enums live in
  `lncrawl/enums.py` and are re-exported from `dao/__init__.py`, which also maintains the
  `models`/`tables` lists Alembic metadata uses.
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
4. **Adding a member to an existing enum needs no migration** — enum columns are plain
   `SMALLINT`/`VARCHAR` (see the enum bullet above), so new members just work. The legacy
   `sync_*` revisions and `2026_07_14_*_drop_native_enums` are the historical record of
   removing the native types; don't add new enum-sync migrations.
5. Verify: `uv run python -m lncrawl dev migrate verify` (upgrades to head + strict schema
   check — this is also the CI gate). Local apply/rollback/status:
   `dev migrate up` / `dev migrate down` / `dev migrate status`.

## Dialect notes

- SQLite is the default (`sqlite.db` in the data dir); `DATABASE_URL` switches to
  Postgres/MySQL. `env.py` enables `render_as_batch` only on SQLite (table-rebuild for
  ALTER/DROP support) — write normal Alembic ops and let batch mode handle it.
- Session pattern in services: `with ctx.db.session() as sess:` — `expire_on_commit=False`
  and **no auto-commit**; every writer calls `sess.commit()` explicitly.
