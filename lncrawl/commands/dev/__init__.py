import typer

from .migrate import app as migrate
from .sources import check_sources

app = typer.Typer(
    help="Run development commands.",
    no_args_is_help=True,
)

app.add_typer(migrate, name="migrate")
app.command(
    "check-sources",
    help="Import and instantiate every source crawler offline.",
)(check_sources)


@app.callback()
def dev():
    pass
