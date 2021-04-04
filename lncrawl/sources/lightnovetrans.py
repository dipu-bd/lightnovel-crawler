# -*- coding: utf-8 -*-
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)

class LNTCrawler(Crawler):
    base_url = 'https://lightnovelstranslations.com/'

    def __parse_toc(self, soup):
        '''parse and return the toc list'''

        volumes = []
        chapters = []

        for div in soup.select('div.su-accordion'):
            vol = div.select('div.su-spoiler-title strong')[1].text.strip()
            vol_id = int(vol) if vol.isdigit() else len(volumes) + 1
            volumes.append(
                {
                    'id': vol_id,
                    'title': vol,
                }
            )
            for a in div.select('.su-spoiler-content p a'):
                chapters.append(
                    {
                        'id': len(chapters) + 1,
                        'volume': vol_id,
                        'title': a.text.strip(),
                        'url': self.absolute_url(a['href']),
                    }
                )
            # end for
        # end for
        return (volumes, chapters)

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        # NOTE: No covers on site, could not grab author name.

        # Extract volume-wise chapter entries
        # chapter_urls = set([])
        self.volumes, self.chapters = self.__parse_toc(soup)

    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting: %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('.entry-content')

        for bad in content.select(
            '.alignleft, .alignright, hr, p[style*="text-align: center"]'
        ):
            bad.decompose()
        # end for

        return str(content)

    # end def


# end class