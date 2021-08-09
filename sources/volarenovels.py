# -*- coding: utf-8 -*-
import json
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

book_url = 'https://www.volarenovels.com/novel/%s'
search_url = 'https://www.volarenovels.com/api/novels/search?query=%s&count=5'


class VolareNovelsCrawler(Crawler):
    base_url = 'https://www.volarenovels.com/'

    def __parse_toc(self, soup):
        '''parse and return the toc list'''

        volumes = []
        chapters = []

        for div in soup.select('#TableOfContents #accordion .panel'):
            vol = div.select('h4.panel-title span')[0].text.strip()
            vol_id = int(vol) if vol.isdigit() else len(volumes) + 1
            volumes.append(
                {
                    'id': vol_id,
                    'title': div.select_one('h4.panel-title .title a').text.strip(),
                }
            )
            for a in div.select('.list-chapters li a'):
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

    def search_novel(self, query):
        '''Gets a list of {title, url} matching the given query'''
        url = search_url % query
        logger.info('Visiting %s ...', url)
        data = self.get_json(url)['items'][:5]
        # logger.debug(data)
        results = []
        for item in data:
            results.append({
                'title': item['name'],
                'url': book_url % item['slug'],
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('#content-container h3.title').text
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_author = soup.select('#content-container .p-tb-10-rl-30 p')[
                1
            ].text.strip()
        except Exception:
            pass  # not so important to raise errors
        # end try
        logger.info('Novel author: %s', self.novel_author)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('#content-container .md-d-table img')['src']
            )
        except Exception:
            pass  # not so important to raise errors
        # end try
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        # chapter_urls = set([])
        self.volumes, self.chapters = self.__parse_toc(soup)

    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting: %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('.fr-view:not(.hidden)')

        for bad in content.select(
            '.chapter-nav, .hidden-text, .__cf_email__, p[data-f-id=\'pbf\'], span[style*="font-size: 0"]'
        ):
            bad.extract()
        # end for

        return str(content)

    # end def


# end class
