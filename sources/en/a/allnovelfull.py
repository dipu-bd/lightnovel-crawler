# -*- coding: utf-8 -*-

import logging
from urllib.parse import quote

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class AllNovelFullCrawler(Crawler):
    base_url = [
        'https://allnovelfull.com/',
    ]

    def search_novel(self, query):
        soup = self.get_soup(self.home_url + 'search?keyword=' + quote(query))

        results = []
        for div in soup.select('.list-truyen > .row'):
            a = div.select_one('.truyen-title a')
            if not isinstance(a, Tag):
                continue
            # end if
            info = div.select_one('.text-info .chapter-text')
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': info.text.strip() if info else '',
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        image = soup.select_one('.info-holder .book img')
        assert isinstance(image, Tag), 'No title found'

        self.novel_title = image['alt']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        authors = soup.select('.info-holder .info a[href*="/author/"]')
        self.novel_author = ', '.join([a.text.strip() for a in authors])
        logger.info('Novel author: %s', self.novel_author)

        logger.info('Getting chapters...')
        possible_id = soup.select_one('input#truyen-id')
        assert possible_id, 'No novel id'
        self.novel_id = possible_id['value']
        soup = self.get_soup(self.home_url + 'ajax-chapter-option?novelId=%s' % self.novel_id)
        for opt in soup.select('select option'):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({ 'id': vol_id })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': opt.text,
                'url': self.absolute_url(opt['value']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('div#chapter-content')
        return self.cleaner.extract_contents(content)
    # end def
# end class
