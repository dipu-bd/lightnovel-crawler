#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [ranobelib.me](https://www.ranobelib.me/).
"""
import logging
from ..utils.crawler import Crawler
import re

# TODO: Set this to your crawler name for meaningful logging
logger = logging.getLogger("RANOBE_LIB_ME")

# TODO: Copy this file directly to your new crawler. And fill up
#       the methods as described in their todos


class RanobeLibCrawler(Crawler):

    def search_novel(self, query):
        '''Gets a list of results matching the given query'''
        # TODO: Use the `self.novel_url` as a query to find matching novels.
        #       Return the search result as a list of items, containing:
        #         `title` - novel name [required]
        #         `url`   - novel url [required]
        #         `info`  - short description about the novel [optional]
        #       You may throw an Exception or empty list in case of failure.
        #
        # You can put the chapter & volume count or latest chapter names, etc.
        # anything in the short description. Please keep it short. Otherwise,
        # it will look bad on console.
        pass
    # end def

    def read_novel_info(self):

        logger.info('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.manga-title h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.manga__image img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        try:
            self.novel_author = soup.select_one(
                "a[href*=author]").text.strip().title()
            logger.info('Novel author: %s', self.novel_author)
        except Exception as err:
            logger.exception('Failed getting author: %s', self.novel_url)
        # end try

        chapters = soup.select('.chapter-item')
        chapters.reverse()

        volumes = set()
        for a in chapters:
            chap_id = len(self.chapters) + 1

            vol_id = int(a['data-volume'])
            volumes.add(vol_id)

            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a.select_one('a')['href']),
                'title': re.sub(r'\s+',' ',a.select_one('a').text.strip()) or ('Том %d. Глава %d' % (int(vol_id), int(a['data-number']))),
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]

        logger.debug('%d volumes and %d chapters found',
                     len(self.volumes), len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):

        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        div = soup.select_one('.reader-container');

        body = self.extract_contents(div)

        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
