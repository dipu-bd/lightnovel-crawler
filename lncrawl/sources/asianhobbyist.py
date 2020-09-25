# -*- coding: utf-8 -*-
import logging
import re

from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)


class AsianHobbyistCrawler(Crawler):
    base_url = 'https://www.asianhobbyist.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            '#content article .post-title.entry-title a').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = 'N/A'
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('#content article p img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.volumes.append({'id': 1})
        for a in soup.select('#content .tabs .wuji-row ul li a'):
            title = a.text.strip()

            chap_id = len(self.chapters) + 1
            match = re.findall(r'ch(apter)? (\d+)', title, re.IGNORECASE)
            if len(match) == 1:
                chap_id = int(match[0][1])
            # end if

            self.chapters.append({
                'volume': 1,
                'id': chap_id,
                'title': title,
                'url':  self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.debug('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        content = soup.select_one('#content article .entry-content')
        self.clean_contents(content)

        return ''.join([
            str(p) for p in content.select('p')
            if len(p.text.strip()) > 1
        ])
    # end def
# end class
