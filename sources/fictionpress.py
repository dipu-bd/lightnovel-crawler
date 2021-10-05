# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import urlparse
from bs4.element import Tag
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
chapter_url = 'https://www.fictionpress.com/s/%s/%s'
search_url = 'https://www.fictionpress.com/search/?keywords=%s&type=story&match=title&ready=1&categoryid=202'


class FictionPressCrawler(Crawler):
    base_url = 'https://www.fictionpress.com/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for div in soup.select('#content_wrapper .z-list')[:25]:
            a = div.select_one('a.stitle')
            a.select_one('img').extract()
            info = div.select_one('.xgray').text.strip()
            chapters = re.findall(r'Chapters: \d+', info)[0]
            origin_book = re.findall(r'^.+Rated:', info)[0][:-9]
            writer = div.select_one('a[href*="/u/"]').text.strip()
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '%s | %s | By, %s' % (origin_book, chapters, writer)
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            '#profile_top b.xcontrast_txt, #content b').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('#profile_top img.cimage')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
        # end if
        logger.info('Novel cover: %s', self.novel_cover)
        
        possible_author = soup.select_one('#profile_top, #content')
        if isinstance(possible_author, Tag):
            possible_author = possible_author.select_one('a[href*="/u/"]')
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info('Novel author: %s', self.novel_author)

        self.novel_id = urlparse(self.novel_url).path.split('/')[2]
        logger.info('Novel id: %s', self.novel_id)

        if soup.select_one('#pre_story_links'):
            origin_book = soup.select('#pre_story_links a')[-1]
            self.volumes.append({
                'id': 1,
                'title': origin_book.text.strip(),
            })
        else:
            self.volumes.append({'id': 1})
        # end if

        chapter_select = soup.select_one('#chap_select, select#jump')
        if chapter_select:
            for option in chapter_select.select('option'):
                self.chapters.append({
                    'volume': 1,
                    'id': int(option['value']),
                    'title': option.text.strip(),
                    'url':  chapter_url % (self.novel_id, option['value']),
                })
            # end for
        else:
            self.chapters.append({
                'id': 1,
                'volume': 1,
                'url':  self.novel_url,
            })
        # end if
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('#storytext, #storycontent')

        return str(contents)
    # end def
# end class
