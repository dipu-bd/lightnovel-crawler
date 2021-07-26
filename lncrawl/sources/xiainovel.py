# -*- coding: utf-8 -*-
import json
import logging
import re

from bs4 import Comment

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class YukiNovelCrawler(Crawler):
    base_url = 'https://www.xiainovel.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('div.page-header h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = "Translated by XiaiNovel"
        logger.info('Novel author: %s', self.novel_author)

        # NOTE: Can't fetch cover url, as it's listed a base64 code.
        # self.novel_cover = self.absolute_url(
        #     soup.select_one('div.col-md-6 img')['src'])
        # logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select('ul.list-group li a')

        chapters.reverse()

        for a in chapters:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('section#StoryContent')

        for d in contents.findAll('div'):
            d.extract()
        # end for

        for comment in contents.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        # end for

        return str(contents)
    # end def
# end class