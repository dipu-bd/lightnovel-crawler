# -*- coding: utf-8 -*-
import json
import logging
import re
import cssutils
import urllib.parse

from bs4 import BeautifulSoup

from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)


class NovelGoCrawler(Crawler):
    base_url = 'https://novelgo.id/'

    def initialize(self):
        self.home_url = 'https://novelgo.id/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find(
            'h2', {'class': 'novel-title'}).text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one(
            'div.noveils-current-author a').text.strip()
        logger.info('Novel author: %s', self.novel_author)

        #thumbnail = soup.find("div", {"class": "novel-thumbnail"})['style']
        #style = cssutils.parseStyle(thumbnail)
        #url = style['background-image']

        # self.novel_cover = self.absolute_url(
        #    url.replace('url(', '').replace(')', ''))

        thumbnail = soup.find("div", {"class": "novel-thumbnail"})['data-bg']
        self.novel_cover = self.absolute_url(
            thumbnail.replace('url(', '').replace(')', ''))
        logger.info('Novel cover: %s', self.novel_cover)

        path = urllib.parse.urlsplit(self.novel_url)[2]
        book_id = path.split('/')[2]
        logger.info(
            'Novel chapter list : https://novelgo.id/wp-json/noveils/v1/chapters?paged=1&perpage=10000&category=%s', book_id)
        # chapter_list = js = self.scraper.post(
        #    'https://novelgo.id/wp-admin/admin-ajax.php?action=LoadChapter&post=%s' % book_id).content
        # chapter_list = js = self.scraper.post(
        #    'https://novelgo.id/wp-json/noveils/v1/chapters?paged=1&perpage=10000&category=%s' % book_id).content
        #soup_chapter = BeautifulSoup(chapter_list, 'lxml')

        #chapters = soup_chapter.select('ul li a')

        # for x in chapters:
        #    chap_id = len(self.chapters) + 1
        #    if len(self.chapters) % 100 == 0:
        #        vol_id = chap_id//100 + 1
        #        vol_title = 'Volume ' + str(vol_id)
        #        self.volumes.append({
        #            'id': vol_id,
        #            'title': vol_title,
        #        })
        #    # end if
        #    self.chapters.append({
        #        'id': chap_id,
        #        'volume': vol_id,
        #        'url': self.absolute_url(x['href']),
        #        'title': x.text.strip() or ('Chapter %d' % chap_id),
        #    })
        # end for

        data = self.get_json(
            'https://novelgo.id/wp-json/noveils/v1/chapters?paged=1&perpage=10000&category=%s' % book_id)

        for chapter in data:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  chapter['permalink'],
                'title': chapter['post_title'] or ('Chapter %d' % chap_id),
            })
            # end for
        # end for

        logger.debug(self.chapters)
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]

        contents = soup.find(
            'div', {'id': 'chapter-post-content'}).findAll('p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
