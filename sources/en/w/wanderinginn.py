# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class WanderingInnCrawler(Crawler):
    base_url = [
        'https://wanderinginn.com/'
    ]

    def initialize(self) -> None:
        self.cleaner.blacklist_patterns.update([
            "Previous Chapter",
            "Table of Contents",
            "Next Chapter"
        ])
    # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:site_name"]')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title['content']
        logger.info('Novel title: %s', self.novel_title)

        possible_novel_cover = soup.select_one('meta[property="og:image"]')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover['content'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "Written by Pirateaba"
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.entry-content a[href*="wanderinginn"]')

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

        body_parts = soup.select_one('div.entry-content')

        return self.cleaner.extract_contents(body_parts)
    # end def
# end class