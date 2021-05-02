# -*- coding: utf-8 -*-
"""
To search for novels in selected sources
"""
import logging
import os
from concurrent import futures

from progress.bar import IncrementalBar
from slugify import slugify

from ..sources import crawler_list

logger = logging.getLogger(__name__)

executor = futures.ThreadPoolExecutor(20)


def get_search_result(app, link, bar):
    try:
        crawler = crawler_list[link]
        instance = crawler()
        instance.home_url = link.strip('/')
        results = instance.search_novel(app.user_input)
        logger.debug(results)
        logger.info('%d results from %s', len(results), link)
        return results
    except Exception:
        import traceback
        logger.debug(traceback.format_exc())
    finally:
        app.progress += 1
        bar.next()
    # end try
    return []
# end def


def process_results(combined_results):
    combined = dict()
    for result in combined_results:
        key = slugify(result['title'])
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
    if not app.crawler_links:
        return

    bar = IncrementalBar('Searching', max=len(app.crawler_links))
    if os.getenv('debug_mode') == 'yes':
        bar.next = lambda n=1: None  # Hide in debug mode
    else:
        bar.start()
    # end if

    # Add future tasks
    checked = {}
    futures_to_check = []
    app.progress = 0
    for link in app.crawler_links:
        crawler = crawler_list[link]
        if crawler in checked:
            logger.info('A crawler for "%s" already exists', link)
            bar.next()
            continue
        # end if
        checked[crawler] = True
        future = executor.submit(get_search_result, app, link, bar)
        futures_to_check.append(future)
    # end for

    # Resolve all futures
    combined_results = [
        item
        for f in futures_to_check
        for item in f.result()
    ]

    # Process combined search results
    app.search_results = process_results(combined_results)
    bar.clearln()
    bar.finish()
    print('Found %d results' % len(app.search_results))
# end def
