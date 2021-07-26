# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class LiberSparkCrawler(Crawler):
    base_url = 'http://liberspark.com/'

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.novel-main-wrapper h1')
        for bad in possible_title.select('span'):
            bad.extract()
        # end for
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('#uploaded-cover-image')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select_one(
            '.novel-author-info a h4').text.strip()
        logger.info('Novel author: %s', self.novel_author)

        for a in reversed(soup.select('#novel-chapters-list td a')):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({'id': vol_id})
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        body = ''
        for p in soup.select('#reader-content > p'):
            for strong in p.select('strong'):
                strong.name = 'span'
            # end for
            if p.text.strip():
                body += str(p).strip()
            # end if
        # end for

        body += '<p>*******</p>'
        for p in soup.select('#authors_note > p'):
            if p.text.strip():
                body += str(p).strip()
            # end if
        # end for

        return body
    # end def
# end class
