import logging
from functools import cached_property
from pathlib import Path
from typing import Mapping, Optional, Sequence
from urllib.parse import urlparse

import sqlmodel as sa
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from ..context import ctx

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

             conn.exec_driver_sql(
                 "INSERT INTO table (id, value) VALUES (?, ?)", (1, "v1")
             )

        """
        with self.engine.connect() as conn:
            return conn.exec_driver_sql(raw_sql, parameters, execution_options)

    # ------------------------------------------------------------------ #
    #                          Prepare Database                          #
    # ------------------------------------------------------------------ #

    def bootstrap(self):
        self._ensure_database()
        base = self.base_revision()
        if base and self.has_any_tables() and not self.current_revision():
            command.stamp(self.alembic_config, base)
        command.upgrade(self.alembic_config, "head")

    @cached_property
    def alembic_config(self) -> Config:
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
        return ScriptDirectory.from_config(self.alembic_config)

    def base_revision(self):
        return self.alembic_script.get_base()

    def latest_revision(self):
        return self.alembic_script.get_current_head()

    def has_any_tables(self):
        with self.engine.connect() as conn:
            return bool(sa.inspect(conn).get_table_names())

    def current_revision(self):
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

    def _ensure_database(self, max_retries=10) -> None:
        """Create the database if it doesn't exist (MySQL and PostgreSQL only)."""
        db_url = ctx.config.db.url
        logger.info(f'Database URL: "{db_url}"')

        # Parse the database URL
        parsed = urlparse(db_url)
        scheme = parsed.scheme
        database = parsed.path.lstrip("/")
        if not database:
            raise ValueError("No database name found in the URL")

        # Create a connection URL without the database name
        if "mysql" in scheme:
            server_url = db_url.replace(f"/{database}", "")
            check_query = sa.text(
                "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db_name"
            )
            create_query = sa.text(
                f"CREATE DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        elif "postgres" in scheme:
            server_url = db_url.replace(f"/{database}", "/postgres")
            check_query = sa.text("SELECT 1 FROM pg_database WHERE datname = :db_name")
            create_query = sa.text(f'CREATE DATABASE "{database}"')
        elif "sqlite" in scheme:
            return  # sqlite doesn't need database creation
        else:
            raise ValueError("Unsupported database")

        # Try to connect to the server and check/create database
        engine = self._create_engine(
            server_url,
            isolation_level="AUTOCOMMIT",
        )
        for attempt in range(1, max_retries + 1):
            try:
                with engine.connect() as conn:
                    logger.info(f"Ensuring database '{database}' exists...")
                    result = conn.execute(check_query, {"db_name": database})
                    exists = result.fetchone() is not None
                    if not exists:
                        logger.info(f"Creating database '{database}'.")
                        conn.execute(create_query)
                        logger.info(f"Database '{database}' created.")
                engine.dispose()
                return
            except Exception as e:
                if attempt == max_retries:
                    logger.warning(f"Failed to ensure database exists. {e}")
                else:
                    logger.info(f"Failed to ensure database. Retrying... {attempt}/{max_retries}")
