# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import quote, urlparse
import urllib.parse
from bs4 import BeautifulSoup

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

#search_url = 'https://www.worldnovel.online/wp-json/writerist/v1/novel/search?keyword=%s'
#chapter_list_url = "https://www.worldnovel.online/wp-json/writerist/v1/chapters?category=%s&perpage=4000&order=ASC&paged=1"


class TranslateIndoCrawler(Crawler):
    base_url = 'https://www.translateindo.com/'

    # def search_novel(self, query):
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

        for span in soup.select('div.entry-content p span'):
            possible_author = re.sub(
                r'[\(\s\n\)]+', ' ', span.text, re.M).strip()
            if possible_author.startswith('Author:'):
                possible_author = re.sub('Author:', '', possible_author)
                self.novel_author = possible_author.strip()
                break
            # end if
        # end for
        logger.info('Novel author: %s', self.novel_author)

        for div in soup.select('.cl-lists .cl-block'):
            possible_vol = div.select_one('.cl-header')
            if not possible_vol:
                continue

            vol_title = possible_vol.text.strip()
            vol_id = len(self.volumes) + 1
            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })

            for a in div.select('ol.cl-body li a'):
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'url':  self.absolute_url(a['href']),
                    'title': a.text.strip() or ('Chapter %d' % chap_id),
                })
            # end for
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
