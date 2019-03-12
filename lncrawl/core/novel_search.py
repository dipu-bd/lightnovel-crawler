#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To search for novels in selected sources
"""
import os
import logging
from concurrent import futures

from slugify import slugify
from progress.bar import IncrementalBar

from ..spiders import crawler_list

logger = logging.getLogger('SEARCH_NOVEL')


def get_search_result(app, link):
    try:
        crawler = crawler_list[link]
        instance = crawler()
        instance.home_url = link.strip('/')
        results = instance.search_novel(app.user_input)
        logger.debug(results)
        logger.info('%d results from %s', len(results), link)
        return results
    except Exception as ex:
        logger.exception(ex)
        return []
    # end try
# end def


def process_results(app, combined_results):
    app.search_results = dict()
    for result in combined_results:
        key = slugify(result['title'])
        if len(key) <= 1:
            continue
        elif key not in app.search_results:
            app.search_results[key] = []
        # end if
        app.search_results[key].append(result)
    # end for

    if len(app.search_results.keys()) == 0:
        raise Exception('No results for: %s' % app.user_input)
    # end if

    logger.debug(app.search_results)
# end def


def search_novels(app):
    executor = futures.ThreadPoolExecutor(10)

    # Add future tasks
    checked = {}
    futures_to_check = {}
    for link in app.crawler_links:
        crawler = crawler_list[link]
        if crawler in checked:
            logger.info('A crawler for "%s" already exists', link)
            continue
        # end if
        checked[crawler] = True
        futures_to_check[
            executor.submit(
                get_search_result,
                app,
                link
            )
        ] = str(crawler)
    # end for

    bar = IncrementalBar('Finding novels', max=len(futures_to_check.keys()))
    bar.start()

    if os.getenv('debug_mode') == 'yes':
        bar.next = lambda: None  # Hide in debug mode
    # end if

    # Resolve future tasks
    app.progress = 0
    combined_results = []
    for future in futures.as_completed(futures_to_check):
        combined_results += future.result()
        app.progress += 1
        bar.next()
    # end for

    # Process combined search results
    process_results(app, combined_results)
    bar.finish()

    executor.shutdown()
# end def
