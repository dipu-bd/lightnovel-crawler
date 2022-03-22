# -*- coding: utf-8 -*-
from lncrawl.core.crawler import Crawler
import requests
import re
import logging
import json


logger = logging.getLogger(__name__)


class ChineseFantasyNovels(Crawler):
    base_url = 'https://m.chinesefantasynovels.com/'

    def read_novel_info(self):
        if not self.novel_url.endswith('/'):
            self.novel_url += '/'
        # end if
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.btitle h1')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('.bookinfo .status').text
        logger.info('%s', self.novel_author)

        volumes = set([])
        for a in reversed(soup.select('dl.chapterlist a')):
            ch_title = a.text.strip()
            ch_id = [int(x) for x in re.findall(r'\d+', ch_title)]
            ch_id = ch_id[0] if len(ch_id) else len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append({
                'id': ch_id,
                'volume': vol_id,
                'title': ch_title,
                'url': self.absolute_url(a['href']),
            })
        # end def

        self.volumes = [{'id': x, 'title': ''} for x in volumes]
    # end def

    def initialize(self) -> None:
        self.cleaner.bad_css.update([
            '.link'
        ])
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('#BookText')
        return self.cleaner.extract_contents(content)
    # end def
# end class
