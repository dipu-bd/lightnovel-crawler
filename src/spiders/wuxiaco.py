#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [WuxiaWorld](http://www.wuxiaworld.co/).
"""
import json
import logging
import re

from bs4 import BeautifulSoup

from ..utils.crawler import Crawler

logger = logging.getLogger('WUXIA_WORLD')
search_url = 'https://m.wuxiaworld.co/SearchBook.aspx'


class WuxiaCoCrawler(Crawler):
    def initialize(self):
        self.home_url = 'https://www.wuxiaworld.co/'
    # end def

    def search_novel(self, query):
        '''Gets a list of {title, url} matching the given query'''
        response = self.submit_form(search_url, data=dict(keyword=query, t=1))
        soup = BeautifulSoup(response.text, 'lxml')

        results = []
        for div in soup.select('.recommend .hot_sale'):
            a = div.select_one('a')
            title = a.select_one('.title').text.strip()
            info = ' | '.join([
                x.text.strip() for x in a.select('.author')
            ])
            results.append({
                'title': title,
                'url': self.absolute_url(a['href']),
                'info': info,
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url.replace('https://m', 'https://www')
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        self.novel_title = soup.select_one('#maininfo h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('#maininfo p').text.strip()
        self.novel_author = re.sub(
            r'^Author[^\w]+', '', self.novel_author).strip()
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('#sidebar img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        last_vol = -1
        volume = {'id': 0, 'title': 'Volume 1', }
        for item in soup.select('#list dl *'):
            if item.name == 'dt':
                vol = volume.copy()
                vol['id'] += 1
                vol['title'] = item.text.strip()
                #vol['title'] = re.sub(r'^(.*)', '', vol['title'])
                #vol['title'] = re.sub(
                #    r'^\s*Text\s*$', '', vol['title']).strip()
                volume = vol
            # end if
            if item.name == 'dd':
                a = item.select_one('a')
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': volume['id'],
                    'title': a.text.strip(),
                    'url':  self.absolute_url(a['href']),
                })
                if last_vol != volume['id']:
                    last_vol = volume['id']
                    self.volumes.append(volume)
                # end if
            # end if
        # end for

        logger.info('%d chapters and %d volumes found',
                    len(self.chapters), len(self.volumes))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]
        body_parts = soup.select_one('div#content')
        body = self.extract_contents(body_parts)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
