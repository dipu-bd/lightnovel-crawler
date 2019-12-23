#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [translateindo.com](https://www.translateindo.com/).
"""
import logging
import re
from urllib.parse import quote, urlparse
import urllib.parse
from bs4 import BeautifulSoup

from ..utils.crawler import Crawler

logger = logging.getLogger('TRANSLATEINDO')

#search_url = 'https://www.worldnovel.online/wp-json/writerist/v1/novel/search?keyword=%s'
#chapter_list_url = "https://www.worldnovel.online/wp-json/writerist/v1/chapters?category=%s&perpage=4000&order=ASC&paged=1"


class TranslateIndoCrawler(Crawler):
    #def search_novel(self, query):
    #    data = self.get_json(search_url % quote(query))

    #    results = []
    #    for item in data:
    #        results.append({
    #            'url': item['permalink'],
    #            'title': item['post_title'],
    #        })
    #    # end for

    #    return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1.entry-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_cover = soup.select_one('div.entry-content img')['src']
        if possible_cover:
            self.novel_cover = self.absolute_url(possible_cover)
        # end if
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select_one('div.entry-content p span').text.strip().replace('Author: ','')
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.select_one('div#comments').find_previous_sibling('div').select('a')

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
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select('div.entry-content p')

        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
