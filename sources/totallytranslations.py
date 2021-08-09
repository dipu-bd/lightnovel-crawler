# -*- coding: utf-8 -*-
import json
import logging
import re

from requests.sessions import Session

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class TotallyTranslations(Crawler):
    base_url = 'https://totallytranslations.com/'

    def initialize(self):
        self.scraper = Session()
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.novel-image img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for p in soup.select('.chapters-list .chapters-title'):
            vol_title = p.text.strip()
            vol_id = len(self.volumes) + 1
            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })

            ul = p.find_next('ul')
            for a in ul.select('a'):
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url':  self.absolute_url(a['href']),
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        paras = soup.select('.post-content p')
        return '\n'.join([str(p) for p in paras if p.text.strip()])
    # end def
# end class
