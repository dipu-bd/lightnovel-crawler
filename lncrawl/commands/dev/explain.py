from rich import print
from rich.markup import escape
import typer

from ...context import ctx


def explain(
    url: str = typer.Argument(help="Any URL on the source to describe."),
):
    ctx.sources.load(sync_remote=False)
    ctx.sources.ensure_load()
    crawler = ctx.sources.init_crawler(url)
    try:
        print(escape(crawler.scraper.explain(url)))
    finally:
        crawler.close()
