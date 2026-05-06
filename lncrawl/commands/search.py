import logging
from concurrent.futures import Future
from difflib import SequenceMatcher
from threading import Event
from typing import List, Optional

import questionary
import typer
from rich import print
from slugify import slugify

from ..context import ctx
from ..core import CombinedSearchResult, SearchResult, TaskManager
from ..server.models import SourceItem

app = typer.Typer(
    help="Search for novels across multiple sources.",
)
logger = logging.getLogger(__name__)


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
    # Prompt for query if not provided
    if not query:
        query = _prompt_query()

    # Validate query
    query = (query or "").strip()
    if len(query.strip()) < 2:
        print("[red]Search query must be at least 2 characters long[/red]")
        raise typer.Exit(1)

    # setup context
    ctx.setup()
    ctx.sources.ensure_load()

    # Get searchable crawlers
    sources = ctx.sources.list(source_query, can_search=True)
    if not sources:
        print("[red]No searchable sources available[/red]")
        raise typer.Exit(1)

    # Perform search
    results = _perform_search(
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


def _prompt_query() -> str:
    return questionary.text(
        qmark="🔍",
        message="Search query:",
        validate=lambda x: (
            True if x and len(x.strip()) >= 2 else "Search query must be at least 2 characters long"
        ),
    ).unsafe_ask()


def _perform_search(
    query: str,
    sources: List[SourceItem],
    limit: int,
    concurrency: int,
    timeout: float,
) -> List[CombinedSearchResult]:
    """Perform the actual search across sources."""
    logger.info(f'Searching {len(sources)} sources for "{query}"')
    signal = Event()
    taskman = TaskManager(concurrency, signal=signal)

    # Submit search tasks
    futures: List[Future[List[SearchResult]]] = []
    for source in sources:
        future = taskman.submit_task(_search_job, source, query, signal)
        futures.append(future)

    # Wait for all tasks to finish with progress
    records: List[SearchResult] = []
    try:
        for result_list in taskman.resolve(
            futures,
            unit="source",
            desc="Searching",
            signal=signal,
            timeout=timeout,
        ):
            records.extend(result_list or [])
    except KeyboardInterrupt:
        signal.set()
    except Exception:
        logger.error("Failed to perform search!", exc_info=ctx.logger.is_info)
    finally:
        signal.set()
        taskman.shutdown()

    # Combine the search results
    combined: dict[str, List[SearchResult]] = {}
    for item in records:
        if not (item and isinstance(item.title, str)):
            continue
        item.title = str(item.title).strip()
        item.info = str(item.info).strip()
        key = slugify(item.title)
        if len(key) <= 2:
            continue
        combined.setdefault(key, [])
        combined[key].append(item)

    # Process combined search results
    results: List[CombinedSearchResult] = []
    for key, value in combined.items():
        value.sort(key=lambda x: x.url)
        combined = CombinedSearchResult(
            id=key,
            novels=value,
            title=value[0].title,
        )
        results.append(combined)

    # Sort by relevance (number of sources, then similarity to query)
    results.sort(
        key=lambda x: (
            -len(x.novels),
            -SequenceMatcher(a=x.title, b=query).ratio(),
        )
    )

    return results[:limit]


def _search_job(source: SourceItem, query: str, signal: Event) -> List[SearchResult]:
    url = source.url
    logger.info(f"[green]{url}[/green] Searching...")
    try:
        setattr(source.crawler, "url", url)
        crawler = ctx.sources.init_crawler(source.crawler)
        crawler.scraper.signal = signal
        results = crawler.search(query)
        results = [SearchResult(**item) for item in results]
        logger.info(f"[green]{url}[/green] Found {len(results)} results")
        crawler.close()
        return results
    except KeyboardInterrupt:
        raise
    except Exception:
        logger.info(f"[green]{url}[/green] Search failed", exc_info=ctx.logger.is_debug)
    return []
