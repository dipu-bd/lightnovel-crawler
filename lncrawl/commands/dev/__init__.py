import typer

from .chapters import recover_empty_chapters
from .explain import explain
from .migrate import app as migrate
from .shadow import shadow_dump
from .sources import check_sources

app = typer.Typer(
    help="Run development commands.",
    no_args_is_help=True,
)

app.add_typer(migrate, name="migrate", hidden=True)

app.command(
    "check-sources",
    help="Import and instantiate every source crawler offline.",
)(check_sources)

app.command(
    "explain",
    help="Describe what the scraper has learned about a URL's origin.",
)(explain)

app.command(
    "shadow-dump",
    help="Read a novel with whichever tier serves it and print it as JSON.",
)(shadow_dump)

app.command(
    "recover-empty-chapters",
    help="Find chapters stored with an empty body and let them be fetched again.",
)(recover_empty_chapters)


@app.callback()
def dev():
    pass
