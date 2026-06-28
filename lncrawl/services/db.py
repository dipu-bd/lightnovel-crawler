from functools import cached_property
import logging
from pathlib import Path
import time
from typing import Any, Mapping, Optional, Sequence

from sqlalchemy.engine import make_url
import sqlmodel as sa

from ..context import ctx
from ..dao import SQLModel

logger = logging.getLogger(__name__)


class DB:
    def __init__(self) -> None:
        pass

    @cached_property
    def engine(self):
        return self._create_engine(ctx.config.db.url)

    def close(self):
        if "engine" in self.__dict__:
            self.engine.dispose()
            self.__dict__.pop("engine")

    def session(
        self,
        *,
        autoflush: bool = True,
        expire_on_commit: bool = False,
        enable_baked_queries: bool = True,
    ):
        return sa.Session(
            self.engine,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
            enable_baked_queries=enable_baked_queries,
        )

    def exec(
        self,
        raw_sql: str,
        parameters: Optional[Sequence] = None,
        execution_options: Optional[Mapping] = None,
    ):
        r"""Executes a string SQL statement on the DBAPI cursor directly,
        without any SQL compilation steps.

         Multiple dictionaries::

             conn.exec_driver_sql(
                 "INSERT INTO table (id, value) VALUES (%(id)s, %(value)s)",
                 [{"id": 1, "value": "v1"}, {"id": 2, "value": "v2"}],
             )

         Single dictionary::

             conn.exec_driver_sql(
                 "INSERT INTO table (id, value) VALUES (%(id)s, %(value)s)",
                 dict(id=1, value="v1"),
             )

         Single tuple::

             conn.exec_driver_sql("INSERT INTO table (id, value) VALUES (?, ?)", (1, "v1"))

        """
        with self.engine.begin() as conn:
            return conn.exec_driver_sql(raw_sql, parameters, execution_options)

    # ------------------------------------------------------------------ #
    #                          Prepare Database                          #
    # ------------------------------------------------------------------ #

    def bootstrap(self, reset_on_failure: bool = False):
        self._ensure_database()
        from alembic import command

        base = self.base_revision()
        if base and self.has_any_tables() and not self.current_revision():
            command.stamp(self.alembic_config, base)

        # Back up the database before running pending migrations so a buggy
        # migration can never destroy a self-hoster's library. Only SQLite is
        # backed up (single file, near-free); skipped when already at head.
        backup = None
        if self.current_revision() != self.latest_revision():
            backup = self._backup_database()

        try:
            command.upgrade(self.alembic_config, "head")
            logger.info("Database bootstrap successful.")
            self._verify_schema()
        except Exception:
            logger.exception("Database bootstrap failed.")
            # Prefer restoring the pre-migration backup over dropping data.
            if self._restore_database(backup):
                raise
            if not reset_on_failure:
                raise
            self._reset_database()
            self.bootstrap()
        else:
            self._discard_backup(backup)

    @cached_property
    def alembic_config(self):
        from alembic.config import Config

        cfg = Config()
        migration_path = Path(__file__).parent.parent / "migrations"
        cfg.set_main_option("sqlalchemy.url", ctx.config.db.url)
        cfg.set_main_option("dialect", self.engine.dialect.name)
        cfg.set_main_option("script_location", migration_path.as_posix())
        cfg.set_main_option(
            "file_template",
            r"%%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d_%%(minute).2d_%%(second).2d_%%(slug)s",
        )
        cfg.set_section_option("post_write_hooks", "hooks", "black")
        cfg.set_section_option("post_write_hooks", "black.type", "console_scripts")
        cfg.set_section_option("post_write_hooks", "black.entrypoint", "black")
        cfg.set_section_option("post_write_hooks", "black.options", "REVISION_SCRIPT_FILENAME")
        return cfg

    @cached_property
    def alembic_script(self):
        from alembic.script import ScriptDirectory

        return ScriptDirectory.from_config(self.alembic_config)

    def base_revision(self):
        return self.alembic_script.get_base()

    def latest_revision(self):
        return self.alembic_script.get_current_head()

    def has_any_tables(self):
        with self.engine.connect() as conn:
            return bool(sa.inspect(conn).get_table_names())

    def current_revision(self):
        from alembic.runtime.migration import MigrationContext

        with self.engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()

    def _create_engine(self, db_url: str, **kwargs):
        kwargs.setdefault("echo", ctx.logger.is_debug)

        # Connection arguments for database-specific settings
        connect_args: dict = kwargs.setdefault("connect_args", {})
        if "postgres" in db_url or "mysql" in db_url:
            connect_args.setdefault("connect_timeout", ctx.config.db.connect_timeout)

        # Pool configuration for connection management
        kwargs.setdefault("pool_size", ctx.config.db.pool_size)
        kwargs.setdefault("pool_timeout", ctx.config.db.pool_timeout)
        kwargs.setdefault("pool_recycle", ctx.config.db.pool_recycle)

        # Maximum overflow connections allowed
        kwargs.setdefault("max_overflow", ctx.config.db.pool_size * 3)

        # Test connections before using them (handles disconnects gracefully)
        kwargs.setdefault("pool_pre_ping", True)

        # Create the engine
        engine = sa.create_engine(db_url, **kwargs)
        if ctx.logger.is_debug:
            engine.logger = logger

        return engine

    def _sqlite_path(self) -> Optional[Path]:
        url = make_url(ctx.config.db.url)
        if "sqlite" not in url.drivername:
            return None
        if not url.database or url.database == ":memory:":
            return None
        return Path(url.database)

    def _backup_database(self) -> Optional[Path]:
        db_path = self._sqlite_path()
        if not db_path or not db_path.exists():
            return None
        import shutil

        backup_path = db_path.with_name(db_path.name + ".bak")
        self.close()  # flush and release the file handle before copying
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to '{backup_path}'.")
        return backup_path

    def _restore_database(self, backup_path: Optional[Path]) -> bool:
        db_path = self._sqlite_path()
        if not db_path or not backup_path or not backup_path.exists():
            return False
        import shutil

        self.close()  # release the half-migrated database before overwriting
        shutil.copy2(backup_path, db_path)
        logger.warning(
            f"Restored database from '{backup_path}' after a failed migration. "
            "Your data is intact; please report this so the migration can be fixed."
        )
        return True

    def _discard_backup(self, backup_path: Optional[Path]) -> None:
        if not backup_path or not backup_path.exists():
            return
        try:
            backup_path.unlink()
        except OSError:
            logger.debug(f"Could not remove backup '{backup_path}'.")

    def _reset_database(self):
        logger.debug("Resetting database...")
        with self.engine.begin() as conn:
            metadata = sa.MetaData()
            metadata.reflect(bind=conn)
            metadata.drop_all(bind=conn)
        self.close()
        logger.info("Database reset.")

    def _ensure_database(self, max_retries=10) -> None:
        """Create the database if it doesn't exist (MySQL and PostgreSQL only)."""
        url = make_url(ctx.config.db.url)
        logger.info(f"Database: '{url}'")

        scheme = url.drivername
        database = url.database

        if "sqlite" in scheme:
            return

        if not database:
            raise ValueError("No database name found in the URL")

        if "mysql" in scheme:
            server_url = url.set(database=None)
            check_query = sa.text(
                "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db_name"
            )
            create_query = sa.text(
                f"CREATE DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        elif "postgres" in scheme:
            server_url = url.set(database="postgres")
            check_query = sa.text("SELECT 1 FROM pg_database WHERE datname = :db_name")
            create_query = sa.text(f'CREATE DATABASE "{database}"')
        else:
            raise ValueError(f"Unsupported database scheme: {scheme}")

        engine = self._create_engine(server_url.render_as_string(hide_password=False))
        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(f"Ensuring database '{database}' exists...")
                # AUTOCOMMIT is required for PostgreSQL; it is harmless for MySQL.
                with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                    result = conn.execute(check_query, {"db_name": database})
                    if result.fetchone() is None:
                        logger.info(f"Creating database '{database}'.")
                        conn.execute(create_query)
                        logger.info(f"Database '{database}' created.")
                engine.dispose()
                return
            except BaseException as e:
                if attempt == max_retries:
                    engine.dispose()
                    raise RuntimeError("Could not create database") from e
                logger.critical(
                    f"Could not connect to database. Retrying... ({attempt}/{max_retries})",
                    exc_info=ctx.logger.is_debug,
                )
                time.sleep(1)

    def _verify_schema(self, strict: bool = False):
        logger.debug("Verifying database schema...")
        from alembic.autogenerate import compare_metadata
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy import Enum as SAEnum

        dialect = self.engine.dialect.name

        def _compare_type(*args):
            # SQLite has no native enum type — enums are stored as VARCHAR
            metadata_type = args[4]
            if dialect == "sqlite" and isinstance(metadata_type, SAEnum):
                return False
            return None

        with self.engine.connect() as conn:
            mc = MigrationContext.configure(
                conn,
                opts={
                    "compare_type": _compare_type,
                    # "compare_server_default": True,
                },
            )

            drift = list(compare_metadata(mc, SQLModel.metadata))
            if drift:
                logger.warning(f"Detected {len(drift)} schema drift(s) against models:")
                for op in drift:
                    logger.warning(f"  - {self._format_drift(op)}")
                # In production (startup), drift is non-fatal: the migration ran,
                # and benign SQLite reflection differences must not block the app.
                # Drift is caught in CI via `lncrawl dev migrate verify` (strict).
                if strict:
                    raise ValueError("Database schema is not valid.")
                logger.warning(
                    "Continuing despite schema drift. "
                    "Run 'lncrawl dev migrate verify' to inspect."
                )
            else:
                logger.info("Database schema is valid.")

    @staticmethod
    def _format_drift(op: Any) -> str:
        # alembic groups index/fk diffs inside a single-element list
        if isinstance(op, list):
            return ", ".join(DB._format_drift(x) for x in op)
        if not isinstance(op, tuple) or len(op) < 2:
            return repr(op)

        name, payload = op[0], op[1]
        if name in ("add_table", "remove_table"):
            return f"{name}: {getattr(payload, 'name', payload)}"
        if name in ("add_column", "remove_column") and len(op) >= 4:
            col = op[3]
            return f"{name}: {op[2]}.{col.name} ({col.type})"
        if name.startswith("modify_") and len(op) >= 7:
            _, _schema, table, column, _kwargs, old, new = op[:7]
            return f"{name}: {table}.{column}: {old!r} -> {new!r}"
        if name in ("add_index", "remove_index", "add_fk", "remove_fk"):
            return f"{name}: {getattr(payload, 'name', payload)}"
        return repr(op)
