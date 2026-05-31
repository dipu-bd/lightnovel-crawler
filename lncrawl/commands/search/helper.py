from difflib import SequenceMatcher
import logging
from threading import Event
from typing import TYPE_CHECKING, List

import questionary
from slugify import slugify

from ...context import ctx

if TYPE_CHECKING:
    from ...core import CombinedSearchResult, SearchResult
    from ...server.models import SourceItem

logger = logging.getLogger(__name__)


def prompt_query() -> str:
    return questionary.text(
        qmark="🔍",
        message="Search query:",
        validate=lambda x: (
            True if x and len(x.strip()) >= 2 else "Search query must be at least 2 characters long"
        ),
    ).unsafe_ask()


def perform_search(
    query: str,
    sources: List["SourceItem"],
    limit: int,
    concurrency: int,
    timeout: float,
) -> List["CombinedSearchResult"]:
    """Perform the actual search across sources."""
    from ...core import CombinedSearchResult, TaskManager

    signal = Event()
    taskman = TaskManager(concurrency, signal=signal)

    logger.info(f'Searching {len(sources)} sources for "{query}"')
    futures = [taskman.submit_task(search_job, source, query, signal) for source in sources]

    # Wait for all tasks to finish with progress
    records: List[SearchResult] = []
    try:
        for result in taskman.resolve(
            futures,
            unit="source",
            desc="Searching",
            signal=signal,
            timeout=timeout,
        ):
            records += result or []
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


def search_job(source: "SourceItem", query: str, signal: Event):
    from ...core import SearchResult

    url = source.url
    crawler = ctx.sources.init_crawler(url)
    crawler.scraper.signal = signal
    results = crawler.search(query)
    results = [SearchResult(**item) for item in results]
    crawler.close()
    logger.info(f"[green]{url}[/green] Found {len(results)} results")
    return results
