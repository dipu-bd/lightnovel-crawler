#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import quote
from ..utils.crawler import Crawler

logger = logging.getLogger('MACHINE_NOVEL_TRANSLATION')

search_url = 'https://www.machine-translation.org/novel/search/?keywords=%s'


class MachineTransOrg(Crawler):
    def search_novel(self, query):
        url = search_url % quote(query.lower())
        logger.debug('Visiting: %s', url)
        soup = self.get_soup(url)

        results = []
        for li in soup.select('.book-list-info li'):
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

        self.novel_title = soup.select_one('.title h3 b').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('.title h3 span').text
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('.book-img img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for div in reversed(soup.select('.article-main .slide-box')):
            vol_id = len(self.volumes) + 1
            vol_title = div.select_one('p.v-name').text.strip()
            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })

            for a in reversed(div.select('.slide-item a')):
                ch_title = a.text.strip()
                ch_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': ch_id,
                    'volume': vol_id,
                    'title': ch_title,
                    'url':  self.absolute_url(a['href']),
                })
            # end for
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
        self.clean_contents(body)

        return str(body)
    # end def
# end class
