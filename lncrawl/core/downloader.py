#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To download chapter bodies
"""
import json
import logging
import os
import traceback
from concurrent import futures
from urllib.parse import urlparse

from progress.bar import IncrementalBar

logger = logging.getLogger('DOWNLOADER')


def downlod_cover(app):
    app.book_cover = None
    if app.crawler.novel_cover:
        logger.info('Getting cover image...')
        try:
            ext = urlparse(app.crawler.novel_cover).path.split('.')[-1]
            filename = os.path.join(
                app.output_path, 'cover.%s' % (ext or 'png'))
            if not os.path.exists(filename):
                logger.debug('Downloading cover image')
                response = app.crawler.get_response(app.crawler.novel_cover)
                with open(filename, 'wb') as f:
                    f.write(response.content)
                # end with
                logger.debug('Saved cover: %s', filename)
            # end if
            app.book_cover = filename
        except Exception:
            logger.debug(traceback.format_exc())
        # end try
    # end if
    if not app.book_cover:
        logger.warn('No cover image')
    # end if
# end def


def download_chapter_body(app, chapter):
    result = None

    dir_name = os.path.join(app.output_path, 'json')
    if app.pack_by_volume:
        vol_name = 'Volume ' + str(chapter['volume']).rjust(2, '0')
        dir_name = os.path.join(dir_name, vol_name)
    # end if
    os.makedirs(dir_name, exist_ok=True)

    chapter_name = str(chapter['id']).rjust(5, '0')
    file_name = os.path.join(dir_name, chapter_name + '.json')

    chapter['body'] = ''
    if os.path.exists(file_name):
        logger.debug('Restoring from %s', file_name)
        with open(file_name, 'r') as file:
            old_chapter = json.load(file)
            chapter['body'] = old_chapter['body']
        # end with
    # end if

    if len(chapter['body']) == 0:
        body = ''
        try:
            logger.debug('Downloading to %s', file_name)
            body = app.crawler.download_chapter_body(chapter)
        except Exception:
            logger.debug(traceback.format_exc())
        # end try
        if len(body) == 0:
            result = 'Body is empty: ' + chapter['url']
        else:
            chapter['body'] = '<h3>%s</h3><h1>%s</h1>\n%s' % (
                chapter['volume_title'], chapter['title'], body)
        # end if
        with open(file_name, 'w') as file:
            file.write(json.dumps(chapter))
        # end with
    # end if

    return result
# end def


def download_chapters(app):
    downlod_cover(app)

    bar = IncrementalBar('Downloading chapters', max=len(app.chapters))
    bar.start()

    if os.getenv('debug_mode') == 'yes':
        bar.next = lambda: None  # Hide in debug mode
    # end if

    futures_to_check = {
        app.crawler.executor.submit(
            download_chapter_body,
            app,
            chapter,
        ): str(chapter['id'])
        for chapter in app.chapters
    }

    app.progress = 0
    for future in futures.as_completed(futures_to_check):
        result = future.result()
        if result:
            bar.clearln()
            logger.error(result)
        # end if
        app.progress += 1
        bar.next()
    # end for

    bar.finish()
# end def
