#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [tapread.com](https://www.tapread.com/).
"""
import json
import logging
import re
import urllib.parse
from bs4 import BeautifulSoup
from ..utils.crawler import Crawler

logger = logging.getLogger('TAPREAD')


class TapreadCrawler(Crawler):

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            'div.book-name').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = 'https:%s' % soup.select_one('div.book-img img')['src']
        logger.info('Novel cover: %s', self.novel_cover)

        regex = re.compile(r'[\n\r\t]')
        self.novel_author = regex.sub("", soup.select_one('div.author').text.strip() + ' ' + soup.select_one('div.translator').text.strip())
        logger.info(self.novel_author)

        path = urllib.parse.urlsplit(self.novel_url)[2]
        book_id = path.split('/')[3]

        js = self.scrapper.post(
            "https://www.tapread.com/book/contents?bookId=%s" % book_id)

        data = js.json()

        chapters = data['result']['chapterList']

        for x in chapters:
            chap_id = x['chapterNo']
            if len(self.chapters) % 100 == 0:
                vol_id = int(chap_id)//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': 'https://www.tapread.com/book/chapter?bookId=%s&chapterId=%s' % (x['bookId'], x['chapterId']),
                'title': x['chapterName'],
            })
        # end for

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])

        js = self.scrapper.post(chapter['url'])

        data = js.json()

        logger.debug(data['result']['chapterName'])

        contents = BeautifulSoup(data['result']['content'], 'lxml')

        return contents.prettify()
    # end def
# end class
