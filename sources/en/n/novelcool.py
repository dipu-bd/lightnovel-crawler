# -*- coding: utf-8 -*-
import json
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class NovelCool(Crawler):
    has_manga = True
    base_url = 'https://www.novelcool.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1.bookinfo-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one(
            'span', {'itemprop': 'creator'}).text.strip()
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.bookinfo-pic img')['src'])

        chapters = soup.select('.chapter-item-list a')
        chapters.reverse()

        for x in chapters:
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
                'url': self.absolute_url(x['href']),
                'title': x.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        # FIXME: Chapters title keep getting duplicated, I've tried multiple fixes but nothings worked so far.
        body_parts = soup.select_one('.chapter-reading-section')

        # Removes report button
        for report in body_parts.find('div', {'model_target_name': 'report'}):
            report.extract()
        # end for

        # Removes End of Chapter junk text.
        for junk in body_parts.find('p', {'class': 'chapter-end-mark'}):
            junk.extract()
        # end for

        return self.extract_contents(body_parts)
    # end def
# end class
