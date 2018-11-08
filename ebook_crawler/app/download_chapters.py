#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To download chapter bodies
"""
import json
import os
from concurrent import futures

from progress.bar import IncrementalBar

from ..utils.helper import retrieve_image


def download_chapters(self):
    self.book_cover = None
    if self.crawler.novel_cover:
        self.logger.warn('Getting cover image...')
        try:
            filename = self.crawler.novel_cover.split('/')[-1]
            filename = os.path.join(self.output_path, filename)
            if not os.path.exists(filename):
                self.logger.info('Downloading cover image')
                retrieve_image(self.crawler.novel_cover, filename)
                self.logger.info('Saved cover: %s', filename)
                self.book_cover = filename
            # end if
        except Exception as ex:
            self.logger.error('Failed to get cover: %s', ex)
        # end try
    else:
        self.logger.warn('No cover image.')
    # end if

    bar = IncrementalBar('Downloading chapters', max=len(self.chapters))
    bar.start()
    futures_to_check = {
        self.crawler.executor.submit(
            self.download_chapter_body,
            chapter,
        ): str(chapter['id'])
        for chapter in self.chapters
    }
    for future in futures.as_completed(futures_to_check):
        result = future.result()
        if result:
            bar.clearln()
            self.logger.error(result)
        # end if
        bar.next()
    # end for
    bar.finish()
# end def

def download_chapter_body(self, chapter):
    result = None

    dir_name = os.path.join(self.output_path, 'json')
    if self.pack_by_volume:
        dir_name = os.path.join(dir_name,
            'Volume ' + str(chapter['volume']).rjust(2, '0'))
    # end if
    os.makedirs(dir_name, exist_ok=True)

    chapter_name = str(chapter['id']).rjust(5, '0')
    file_name = os.path.join(dir_name, chapter_name + '.json')

    chapter['body'] = ''
    if os.path.exists(file_name):
        self.logger.info('Restoring from %s', file_name)
        with open(file_name, 'r') as file:
            old_chapter = json.load(file)
            chapter['body'] = old_chapter['body']
        # end with
    if len(chapter['body']) == 0:
        self.logger.info('Downloading to %s', file_name)
        body = self.crawler.download_chapter_body(chapter)
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
