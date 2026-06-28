from alembic import context

from lncrawl.context import ctx
from lncrawl.dao import SQLModel

if context.is_offline_mode():
    raise Exception("Offline mode is not supported")

with ctx.db.engine.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=SQLModel.metadata,
        compare_type=True,
        # SQLite cannot ALTER/DROP columns in place on older versions.
        # Batch mode rebuilds the table, making migrations portable across
        # every bundled SQLite version that desktop self-hosters may have.
        render_as_batch=connection.dialect.name == "sqlite",
    )

    with context.begin_transaction():
        context.run_migrations()
