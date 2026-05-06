import typer
import uvicorn
from typing_extensions import Annotated

from ..context import ctx

app = typer.Typer()


@app.command(help="Run web server.")
def server(
    host: Annotated[str, typer.Option("-h", "--host", help="Server host")] = "0.0.0.0",
    port: Annotated[int, typer.Option("-p", "--port", help="Server port")] = 8181,
    watch: Annotated[bool, typer.Option("-w", "--watch", help="Run server in watch mode")] = False,
    workers: Annotated[int, typer.Option("-n", "--worker", help="Number of workers to run")] = 1,
):
    if watch:
        uvicorn.run(
            "lncrawl.server.app:app",
            workers=workers,
            reload=True,
            port=port,
            host=host,
            access_log=ctx.logger.is_debug,
            log_level=ctx.logger.level or "error",
        )
    else:
        from ..server.app import app as server

        uvicorn.run(
            server,
            port=port,
            host=host,
            access_log=ctx.logger.is_debug,
            log_level=ctx.logger.level or "error",
        )
