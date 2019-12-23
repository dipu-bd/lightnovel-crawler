#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [boxnovel.com](https://boxnovel.com/).
"""
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('WATTPAD')
#search_url = 'https://boxnovel.com/?s=%s&post_type=wp-manga&author=&artist=&release='


class WattpadCrawler(Crawler):

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select('h1')[0].get_text().strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select('div.cover.cover-lg img')[0]['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select('div.author-info strong a')[0].get_text()
        logger.info('Novel author: %s', self.novel_author)

        description = soup.select('h2.description')[0].get_text()

        chapters = soup.select('ul.table-of-contents a')
        #chapters.reverse()

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = chap_id//100 + 1
            if len(self.chapters) % 100 == 0:
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
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
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])

        soup = self.get_soup(chapter['url'])
        pages = int(re.search('[1-9]',re.search('("pages":)([1-9])', str(soup)).group(0)).group(0))
        chapter['title'] = soup.select('h2')[0].get_text().strip()
        contents = []
        for i in range(1, pages+1):
            page_url = chapter['url'] + "/page/" + str(i)
            logger.info('Get body text from %s', page_url)
            soup_page = self.get_soup(page_url)
            for p in soup_page.select('pre p'):
                contents.append(p.text)

        return '<p>' + '</p><p>'.join(contents) + '</p>'
    # end def
# end class
