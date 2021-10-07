# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import quote
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = 'https://www.machine-translation.org/novel/search/?keywords=%s'


class MachineTransOrg(Crawler):
    machine_translation = True
    base_url = 'https://www.machine-translation.org/'

    def search_novel(self, query):
        url = search_url % quote(query.lower())
        logger.debug('Visiting: %s', url)
        soup = self.get_soup(url)

        results = []
        for li in soup.select('.book-list-info > ul > li'):
            results.append({
                'title': li.select_one('a h4 b').text.strip(),
                'url': self.absolute_url(li.select_one('.book-img a')['href']),
                'info': li.select_one('.update-info').text.strip(),
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('div.title h3 b').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('div.title h3 span').text
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('.book-img img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for a in reversed(soup.select('div.slide-item a')):
            ch_title = a.text.strip()
            ch_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = ch_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': ch_id,
                'volume': vol_id,
                'title': ch_title,
                'url':  self.absolute_url(a['href']),
            })
        # end for

        logger.debug('%d chapters and %d volumes found',
                     len(self.chapters), len(self.volumes))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        body = soup.select_one('.read-main .read-context')

        self.blacklist_patterns = [
            r'^Refresh time: \d+-\d+-\d+$'
        ]
        return self.extract_contents(body)
    # end def
# end class
