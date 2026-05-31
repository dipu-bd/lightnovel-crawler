import logging
import os
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from .commands.config import app as config
from .commands.crawl import app as crawl
from .commands.dev import app as dev
from .commands.search import app as search
from .commands.server import app as server
from .commands.sources import app as sources
from .commands.version import app as version
from .context import ctx

logger = logging.getLogger(__name__)

# Define typer
app = typer.Typer(
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
    no_args_is_help=True,
    pretty_exceptions_short=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

# Register subcommands
app.add_typer(version)
app.add_typer(dev, name="dev", hidden=True)
app.add_typer(config, name="config")
app.add_typer(sources, name="sources")
app.add_typer(crawl)
app.add_typer(search)
app.add_typer(server)


# Define main command
@app.callback()
def main(
    context: typer.Context,
    log_level: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-l",
            help="Log levels: -l = warn, -ll = info, -lll = debug",
            show_default=False,
            count=True,
            metavar="",
        ),
    ] = 0,
    config: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            "-c",
            help="Config file",
            show_default=False,
            file_okay=True,
        ),
    ] = None,
):
    # set context object
    context.obj = ctx
    context.call_on_close(ctx.destroy)

    # setup logger
    os.environ["LNCRAWL_LOG_LEVEL"] = str(log_level)
    ctx.logger.setup()

    # load config
    if config:
        os.environ["LNCRAWL_CONFIG"] = str(config)
    ctx.config.load()


@app.command("app", help="Launches the web application.")
def start_app():
    from .server.webview import start

    start()
