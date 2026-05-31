from __future__ import annotations

from typing import Optional

from rich import print
import typer

from ...context import ctx
from .app import app


@app.command(help="Search for novels by query string.")
def search(
    source_query: Optional[str] = typer.Option(
        None,
        "-s",
        "--source",
        help="Filter sources",
    ),
    concurrency: int = typer.Option(
        15,
        "-c",
        "--concurrency",
        min=1,
        max=25,
        help="Maximum number of concurrent searches (default: 25)",
    ),
    limit: int = typer.Option(
        10,
        "-l",
        "--limit",
        min=1,
        max=25,
        help="Maximum number of results to return",
    ),
    timeout: float = typer.Option(
        30,
        "-t",
        "--timeout",
        min=1,
        help="Maximum timeout for each search (default: 30 seconds)",
    ),
    query: Optional[str] = typer.Argument(
        None,
        help="Search query string",
    ),
):
    """
    Search for novels across multiple sources using the given query string.

    Examples:
        lncrawl search "solo leveling"
        lncrawl search "overlord" --source "novelfull"
        lncrawl search "reincarnation" --limit 20 --concurrency 10
    """
    from .helper import perform_search, prompt_query

    # Prompt for query if not provided
    if not query:
        query = prompt_query()

    # Validate query
    query = (query or "").strip()
    if len(query.strip()) < 2:
        print("[red]Search query must be at least 2 characters long[/red]")
        raise typer.Exit(1)

    # setup context
    ctx.setup()
    ctx.sources.ensure_load()

    # Get searchable crawlers
    sources = ctx.sources.list(
        source_query,
        can_search=True,
        include_rejected=False,
    )
    if not sources:
        print("[red]No searchable sources available[/red]")
        raise typer.Exit(1)

    # Perform search
    results = perform_search(
        query=query,
        sources=sources,
        concurrency=concurrency,
        limit=limit,
        timeout=timeout,
    )
    if not results:
        print(f'[yellow]No results found for "{query}"[/yellow]')
        return

    # Print results
    for result in results:
        print(
            f":book: [green bold]{result.title}[/green bold]",
            f" ({len(result.novels)} results)",
        )
        for novel in result.novels:
            print(f"  :right_arrow: [cyan]{novel.url}[/cyan]")
            if novel.info:
                print(f"    [dim]{novel.info}[/dim]")
        print()
