import logging

from sqlmodel import Session, SQLModel, create_engine

from .context import ServerContext

logger = logging.getLogger(__name__)


class DB:
    def __init__(self, ctx: ServerContext) -> None:
        self.engine = create_engine(
            ctx.config.server.database_url,
            echo=logger.isEnabledFor(logging.DEBUG),
        )

    def close(self):
        self.engine.dispose()

    def prepare(self):
        logger.info('Creating tables')
        SQLModel.metadata.create_all(self.engine)

    def session(
        self, *,
        future: bool = True,
        autoflush: bool = True,
        autocommit: bool = False,
        expire_on_commit: bool = True,
        enable_baked_queries: bool = True,
    ):
        return Session(
            self.engine,
            future=future,  # type:ignore
            autoflush=autoflush,
            autocommit=autocommit,  # type:ignore
            expire_on_commit=expire_on_commit,
            enable_baked_queries=enable_baked_queries,
        )
