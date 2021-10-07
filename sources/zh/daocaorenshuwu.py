# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import parse_qsl, urlparse

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class Daocaorenshuwu(Crawler):
    base_url = [
        'https://www.daocaorenshuwu.com/',
    ]

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            '.container .book-info h1.book-name').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select('.container .media-body .row div')[0].text.strip()
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('.container .media-left a img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise ch
        # apter entries
        chapters = soup.select('#all-chapter a')

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
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select('.cont-text > p')
        contents = [str(p) for p in contents if p.text.strip()]
        return ''.join(contents)
    # end def
# end class