from rich import print
from rich.markup import escape
import typer

from ...context import ctx


def explain(
    url: str = typer.Argument(help="Any URL on the source to describe."),
):
    """Describe what the scraper has learned about a URL's origin.

    Deliberately not routed through `init_crawler`, which refuses a rejected host: a
    rejected host is the one whose diagnosis is most worth reading, and a crawler is
    not needed to read it.
    """
    ctx.sources.load(sync_remote=False)
    ctx.sources.ensure_load()

    reason = ctx.sources.is_rejected(url)
    if reason:
        print(f"[yellow]This domain is rejected:[/yellow] {escape(reason)}\n")

    print(escape(ctx.scraper.explain(url)))
