"""
To search for novels in selected sources
"""
import random
import logging
from typing import Dict, List

from concurrent.futures import Future
from slugify import slugify
import difflib

from ..models import CombinedSearchResult, SearchResult
from .sources import crawler_list, prepare_crawler
from .taskman import TaskManager

SEARCH_TIMEOUT = 60
MAX_RESULTS = 15

logger = logging.getLogger(__name__)
taskman = TaskManager(10)


def _perform_search(app, link):
    from .app import App
    assert isinstance(app, App)
    try:
        crawler = prepare_crawler(link)
        results = []
        for item in crawler.search_novel(app.user_input):
            if not isinstance(item, SearchResult):
                item = SearchResult(**item)
            if not (item.url and item.title):
                continue
            results.append(item)
        logger.debug(results)
        logger.info(f"{len(results)} results from {link}")
        return results
    except Exception:
        if logger.isEnabledFor(logging.DEBUG):
            logging.exception("<!> Search Failed! << %s >>", link)
        return []
    finally:
        app.progress += 1


def search_novels(app):
    from .app import App
    assert isinstance(app, App)

    if not app.crawler_links:
        return

    sources = app.crawler_links.copy()
    random.shuffle(sources)

    # Add future tasks
    checked = set()
    app.progress = 0
    futures: List[Future] = []
    for link in sources:
        crawler = crawler_list[link]
        if crawler in checked:
            continue
        checked.add(crawler)
        f = taskman.submit_task(_perform_search, app, link)
        futures.append(f)

    # Resolve all futures
    try:
        taskman.resolve_futures(
            futures,
            desc="Searching",
            unit="source",
            timeout=SEARCH_TIMEOUT,
        )
    except Exception:
        if logger.isEnabledFor(logging.DEBUG):
            logging.exception("<!> Search Failed!")

    # Combine the search results
    combined: Dict[str, List[SearchResult]] = {}
    for f in futures:
        if not f or not f.done() or f.cancelled():
            continue
        for item in f.result() or []:
            if not (item and item.title):
                continue
            key = slugify(str(item.title))
            if len(key) <= 2:
                continue
            combined.setdefault(key, [])
            combined[key].append(item)

    # Process combined search results
    processed: List[CombinedSearchResult] = []
    for key, value in combined.items():
        value.sort(key=lambda x: x.url)
        processed.append(
            CombinedSearchResult(
                id=key,
                title=value[0].title,
                novels=value,
            )
        )
    processed.sort(
        key=lambda x: (
            -len(x.novels),
            -difflib.SequenceMatcher(None, x.title, app.user_input).ratio(),
        )
    )
    app.search_results = processed[:MAX_RESULTS]
