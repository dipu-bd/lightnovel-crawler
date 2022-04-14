# -*- coding: utf-8 -*-
"""
To search for novels in selected sources
"""
import logging
import os
from concurrent import futures

from slugify import slugify
from tqdm import tqdm

from ..core.sources import crawler_list

SEARCH_TIMEOUT = 10

logger = logging.getLogger(__name__)

executor = futures.ThreadPoolExecutor(20)


def get_search_result(app, link, bar):
    try:
        CrawlerType = crawler_list[link]
        instance = CrawlerType()
        instance.home_url = link
        results = instance.search_novel(app.user_input)
        logger.debug(results)
        logger.info('%d results from %s', len(results), link)
        return results
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        if logger.isEnabledFor(logging.DEBUG):
            logging.exception('Searching failure for %s', link)
        # end if
    # end try
    return []
# end def


def process_results(combined_results):
    combined = dict()
    for result in combined_results:
        key = slugify(result.get('title') or '')
        if len(key) <= 2:
            continue
        combined.setdefault(key, [])
        combined[key].append(result)
    # end for

    processed = []
    for key, value in combined.items():
        value.sort(key=lambda x: x['url'])
        processed.append({
            'id': key,
            'title': value[0]['title'],
            'novels': value
        })
    # end for

    processed.sort(key=lambda x: -len(x['novels']))

    return processed[:15]  # Control the number of results
# end def


def search_novels(app):
    from .app import App
    assert isinstance(app, App)

    if not app.crawler_links:
        return

    sources = app.crawler_links.copy()
    #random.shuffle(sources)

    bar = tqdm(desc='Searching',
               total=len(sources), unit='source',
               disable=os.getenv('debug_mode') == 'yes')

    # Add future tasks
    checked = {}
    futures_to_check = []
    app.progress = 0
    for link in sources:
        crawler = crawler_list[link]
        if crawler in checked:
            logger.info('A crawler for "%s" already exists', link)
            bar.update()
            continue
        # end if
        checked[crawler] = True
        future = executor.submit(get_search_result, app, link, bar)
        futures_to_check.append(future)
    # end for

    # Resolve all futures
    combined_results = []
    for i, f in enumerate(futures_to_check):
        assert isinstance(f, futures.Future)
        try:
            f.result(SEARCH_TIMEOUT)
        except KeyboardInterrupt:
            break
        except TimeoutError:
            f.cancel()
        except Exception as e:
            logger.debug('Failed to complete search', e)
        finally:
            app.progress += 1
            bar.update()
        # end try
    # end for

    # Cancel any remaining futures
    for f in futures_to_check:
        assert isinstance(f, futures.Future)
        if not f.done():
            f.cancel()
        elif not f.cancelled():
            combined_results += f.result()
        # end if
    # end for

    # Process combined search results
    app.search_results = process_results(combined_results)
    bar.close()
# end def
