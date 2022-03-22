# -*- coding: utf-8 -*-
import json
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class IndoNovels(Crawler):
    base_url = [
        'http://www.indonovels.net/',
        'https://indonovels.blogspot.co.id/',
    ]

    def initialize(self):
        self.home_url = 'http://www.indonovels.net/'
    # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find(
            "h2", {"style": "text-align: center;"}).text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.separator a')['href'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "Translated by IndoNovels"
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        chapters = soup.find('div', {
            'style': '-goog-ms-box-shadow: 0 0 10px #000000; -moz-box-shadow: 0 0 10px #000000; -webkit-box-shadow: 0 0 10px #000000; border: 6px double #FF00FF; color: #b4040; height: 500px; overflow: auto; padding: 10px; width: 580px;'}).findAll(
            'a')

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({ 'id': vol_id })
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
        soup = self.get_soup(chapter['url'])
        body_parts = soup.select_one('div.post-body-inner')
        return self.cleaner.extract_contents(body_parts)
    # end def
# end class
