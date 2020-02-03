# -*- coding: utf-8 -*-
import logging
import re
import json
from urllib.parse import quote, urlparse
import urllib.parse
from bs4 import BeautifulSoup

from ..utils.crawler import Crawler

logger = logging.getLogger('WORLDNOVEL_ONLINE')

search_url = 'https://www.worldnovel.online/wp-json/writerist/v1/novel/search?keyword=%s'
chapter_list_url = "https://www.worldnovel.online/wp-json/writerist/v1/chapters?category=%s&perpage=100&order=ASC&paged=%s"


class WorldnovelonlineCrawler(Crawler):
    base_url = 'https://www.worldnovel.online/'

    # Disabled because it takes too long to respond
    # def search_novel(self, query):
    #     data = self.get_json(search_url % quote(query))
    #     results = []
    #     for item in data:
    #         results.append({
    #             'url': item['permalink'],
    #             'title': item['post_title'],
    #         })
    #     # end for
    #     return results
    # # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            '.breadcrumb-item.active').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_cover = soup.select_one('img.lazy[alt*="Thumbnail"]')
        if possible_cover:
            self.novel_cover = self.absolute_url(possible_cover['data-src'])
        # end if
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select_one(
            'a[href*="/authorr/"]').text.strip()
        logger.info('Novel author: %s', self.novel_author)

        path = urllib.parse.urlsplit(self.novel_url)[2]
        book_id = path.split('/')[2]
        #book_id = soup.select_one('span.js-add-bookmark')['data-novel']
        logger.info('Bookid = %s' % book_id)

        page = len(soup.select('div.d-flex div.jump-to.mr-2'))

        data = []

        for x in range(page):
            list_url = chapter_list_url % (book_id, x+1)
            logger.debug('Visiting %s', list_url)
            data.extend(self.get_json(list_url))
        # end for

        # if 'code' in data and data['code'] == 'rest_no_route':
        #     chapters = soup.select('div.lightnovel-episode ul li a')
        #     temp_chapters = []
        #     descending = False
        #     for a in chapters:
        #         if 'book' in a.text.strip().lower():
        #             chap_id = len(temp_chapters) + 1
        #             descending = True
        #         else:
        #             try:
        #                 chap_id = int(re.findall(
        #                     r'\d+', a.text.lower().split('chapter', 1)[1])[0])
        #             except Exception:
        #                 chap_id = len(temp_chapters) + 1
        #                 descending = True
        #             # end try
        #         # end if
        #         temp_chapters.append({
        #             'id': chap_id,
        #             'url': a['href'],
        #             'title': a.text.strip(),
        #         })
        #     # end for

        #     if descending:
        #         temp_chapters.reverse()
        #     else:
        #         temp_chapters.sort(key=itemgetter('id'))
        #     # end if

        #     for a in temp_chapters:
        #         chap_id = len(self.chapters) + 1
        #         if len(self.chapters) % 100 == 0:
        #             vol_id = (chap_id - 1) // 100 + 1
        #             vol_title = 'Volume ' + str(vol_id)
        #             self.volumes.append({
        #                 'id': vol_id,
        #                 'title': vol_title,
        #             })
        #         # end if
        #         self.chapters.append({
        #             'id': chap_id,
        #             'volume': vol_id,
        #             'url':  self.absolute_url(a['url']),
        #             'title': a['title'],
        #         })
        #     # end for
        # else:

        volumes = set()
        for item in data:
            vol_id = len(self.chapters) // 100 + 1
            volumes.add(vol_id)
            self.chapters.append({
                'id': len(self.chapters) + 1,
                'volume': vol_id,
                'url': item['permalink'],
                'title': item['post_title'],
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one(', '.join([
            '.post-content'
            '.cha-words',
            '.cha-content',
            '.chapter-fill',
            '.entry-content.cl',
            '#content',
        ]))
        if not contents:
            return ''
        # end if

        # self.clean_contents(contents)

        for codeblock in contents.select('div.code-block'):
            codeblock.decompose()
        # end for

        return str(contents)
    # end def
# end class
