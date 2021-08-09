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
    except Exception as e:
        if logger.isEnabledFor(logging.DEBUG):
            logging.debug('Searching failure for %s', link)
        # end if
    finally:
        app.progress += 1
        bar.update()
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
    if not app.crawler_links:
        return

    bar = tqdm(desc='Searching', total=len(app.crawler_links), unit='')
    if os.getenv('debug_mode') == 'yes':
        bar.update = lambda n=1: None  # Hide in debug mode
    # end if
    bar.clear()

    # Add future tasks
    checked = {}
    futures_to_check = []
    app.progress = 0
    for link in app.crawler_links:
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
    combined_results = [
        item
        for f in futures_to_check
        for item in f.result()
    ]

    # Process combined search results
    app.search_results = process_results(combined_results)
    bar.close()
    print('Found %d results' % len(app.search_results))
# end def
