#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [novelplanet.com](https://novelplanet.com/).
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from .utils.crawler import Crawler

logger = logging.getLogger('NOVEL_PLANET')


class NovelPlanetCrawler(Crawler):
    @property
    def supports_login(self):
        '''Whether the crawler supports login() and logout method'''
        return False
    # end def

    def login(self, email, password):
        pass
    # end def

    def logout(self):
        pass
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        response = self.get_response(self.novel_url)
        soup = BeautifulSoup(response.content, 'lxml')

        self.novel_title = soup.find('a', {'class': 'title'}).text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.post-previewInDetails img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for span in soup.find_all("span", {"class": "infoLabel"}):
            if span.text == 'Author:':
                author = span.findNext('a').text
                author2 = span.findNext('a').findNext('a').text
        # check if author word is found in second <p>
        if (author2 != 'Ongoing') or (author2 != 'Completed'):
            self.novel_author = author + ' (' + author2 + ')'
        else:
            self.novel_author = author
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.find_all('div', {'class': 'rowChapter'})
        chapters.reverse()

        for x in chapters:
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
                'url': self.absolute_url(x.find('a')['href']),
                'title': x.find('a')['title'] or ('Chapter %d' % chap_id),
            })
        # end for

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def
    
    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.content, 'lxml')

        logger.debug(soup.title.string)

        if 'Chapter' in soup.select_one('h3').text:
            chapter['title'] = soup.select_one('h3').text
        else:
            chapter['title'] = chapter['title'] + ' : ' + soup.select_one('h3').text
        # end if

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]

        contents = soup.select_one('#divReadContent').contents
        body = self.extract_contents(contents)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
