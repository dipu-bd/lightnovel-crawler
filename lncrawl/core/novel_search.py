"""
To search for novels in selected sources
"""
import atexit
import logging
import time
from concurrent.futures import Future
from difflib import SequenceMatcher
from multiprocessing import Manager, Process
from typing import Dict, List
from urllib.parse import urlparse

from slugify import slugify

CONCURRENCY = 25
MAX_RESULTS = 10
SEARCH_TIMEOUT = 20

logger = logging.getLogger(__name__)


# This function runs in a separate process
def _search_process(results: list, link: str, file_path: str, query: str):
    try:
        from ..models import SearchResult
        from .sources import prepare_crawler

        crawler = prepare_crawler(link, file_path)
        setattr(crawler, 'can_use_browser', False)  # disable browser in search

        for item in crawler.search_novel(query):
            if not isinstance(item, SearchResult):
                item = SearchResult(**item)
            if not (item.url and item.title):
                continue
            item.title = item.title.lower().title()
            results.append(item)
    except KeyboardInterrupt:
        pass
    except Exception:
        if logger.isEnabledFor(logging.DEBUG):
            logger.exception(f'<< {link} >> Search failed')


# This runs in a thread to execute the processes
def _run(p: Process, hostname: str):
    from .exeptions import LNException
    start_time = time.time()
    try:
        atexit.register(p.kill)
        p.start()
        p.join(SEARCH_TIMEOUT)
        if p.is_alive():
            raise LNException(f"[{hostname}] Timeout")
    finally:
        atexit.unregister(p.kill)
        p.kill()
        run_time = round(time.time() - start_time)
        logging.debug(f"[{hostname}] {run_time} seconds")


def search_novels(app):
    from ..models import CombinedSearchResult, SearchResult
    from .app import App
    from .sources import crawler_list
    from .taskman import TaskManager

    assert isinstance(app, App)

    if not app.crawler_links or not app.user_input:
        return

    manager = Manager()
    results = manager.list()
    taskman = TaskManager(CONCURRENCY)

    # Create tasks for the queue
    checked = set()
    futures: List[Future] = []
    for link in app.crawler_links:
        hostname = urlparse(link).hostname
        CrawlerType = crawler_list.get(hostname or '')
        if CrawlerType in checked:
            continue
        checked.add(CrawlerType)

        p = Process(
            name=hostname,
            target=_search_process,
            args=(
                results,
                link,
                getattr(CrawlerType, 'file_path'),
                app.user_input
            ),
        )

        f = taskman.submit_task(_run, p, hostname)
        futures.append(f)

    # Wait for all tasks to finish
    try:
        app.progress = 0
        for _ in taskman.resolve_as_generator(
            futures,
            unit='source',
            desc='Search',
            timeout=SEARCH_TIMEOUT,
        ):
            app.progress += 1
    except KeyboardInterrupt:
        pass
    except Exception:
        if logger.isEnabledFor(logging.DEBUG):
            logger.exception('Search failed!')

    # Combine the search results
    combined: Dict[str, List[SearchResult]] = {}
    for item in results:
        assert isinstance(item, SearchResult)
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
            -SequenceMatcher(a=x.title, b=app.user_input).ratio(),  # type: ignore
        )
    )
    app.search_results = processed[:MAX_RESULTS]
