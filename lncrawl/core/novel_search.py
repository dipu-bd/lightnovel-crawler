"""
To search for novels in selected sources
"""
import logging
import os
from concurrent import futures
from typing import Dict, List

from slugify import slugify
from tqdm import tqdm

from ..core.sources import crawler_list, prepare_crawler
from ..models import CombinedSearchResult, SearchResult

SEARCH_TIMEOUT = 60

logger = logging.getLogger(__name__)
executor = futures.ThreadPoolExecutor(20)


def _perform_search(app, link, bar):
    try:
        crawler = prepare_crawler(link)
        results = []
        for item in crawler.search_novel(app.user_input):
            if not item.get("url"):
                continue
            if not isinstance(item, SearchResult):
                item = SearchResult(**item)
            results.append(item)

        logger.debug(results)
        logger.info("%d results from %s", len(results), link)
        return results
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        if logger.isEnabledFor(logging.DEBUG):
            logging.exception("<!> Search Failed! << %s >>", link)
        return []


def _combine_results(results: List[SearchResult]) -> List[CombinedSearchResult]:
    combined: Dict[str, List[SearchResult]] = {}
    for item in results:
        key = slugify(item.title)
        if len(key) <= 2:
            continue
        combined.setdefault(key, [])
        combined[key].append(item)

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

    processed.sort(key=lambda x: -len(x.novels))
    return processed[:15]  # Control the number of results


def search_novels(app):
    from .app import App

    assert isinstance(app, App)

    if not app.crawler_links:
        return

    sources = app.crawler_links.copy()
    # random.shuffle(sources)

    is_debug = os.getenv("debug_mode")
    bar = tqdm(
        desc="Searching",
        total=len(sources),
        unit="source",
        disable=is_debug,
    )

    # Add future tasks
    checked = {}
    futures_to_check = []
    app.progress = 0
    for link in sources:
        crawler = crawler_list[link]
        if crawler in checked:
            bar.update()
            continue
        checked[crawler] = True
        future = executor.submit(_perform_search, app, link, bar)
        futures_to_check.append(future)

    # Resolve all futures
    results: List[SearchResult] = []
    for i, f in enumerate(futures_to_check):
        assert isinstance(f, futures.Future)
        try:
            f.result(SEARCH_TIMEOUT)
        except KeyboardInterrupt:
            break
        except TimeoutError:
            f.cancel()
        except Exception as e:
            if is_debug:
                logger.error("Failed to complete search", e)
        finally:
            app.progress += 1
            bar.update()

    # Cancel any remaining futures
    for f in futures_to_check:
        assert isinstance(f, futures.Future)
        if not f.done():
            f.cancel()
        elif not f.cancelled():
            results += f.result()

    # Process combined search results
    app.search_results = _combine_results(results)
    bar.close()
