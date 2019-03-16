#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [worldnovel.online](https://www.worldnovel.online/).
"""
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('WORLDNOVEL_ONLINE')
search_url = 'https://www.worldnovel.online/?s=%s'


class WorldnovelonlineCrawler(Crawler):
    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select('article div h3 a')[:5]:
            url = self.absolute_url(a['href'])
            results.append({
                'url': url,
                'title': self.trim_search_title(a.text.strip()),
                'info': self.search_novel_info(url),
            })
        # end for

        return results
    # end def

    def search_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        #score = soup.select_one('span.star')['data-content']

        chapters = soup.select('div.lightnovel-episode ul li a')
        info = '%d chapters' % len(chapters)

        if len(chapters) > 0:
            info += ' | Latest: %s' % chapters[0].text.strip()
        # end if

        return info
    # end def

    def trim_search_title(self, title):
        '''Trim title search result'''
        removal_list = ['Novel', 'Bahasa', 'Indonesia']
        edit_string_as_list = title.split()
        final_list = [
            word for word in edit_string_as_list
            if word not in removal_list
        ]
        final_string = ' '.join(final_list)
        return final_string
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            'h1.elementor-heading-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('div', {'class': 'elementor-image'}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.select('div.elementor-shortcode p')[1].findAll('a')
        if len(author) == 2:
            self.novel_author = author[0].text + ' (' + author[1].text + ')'
        else:
            self.novel_author = ''
            for a in author:
                self.novel_author = self.novel_author + a.text + ' '
            # end for
        # end if
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.select('div.lightnovel-episode ul li a')

        chapters.reverse()

        for a in chapters:
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
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        logger.debug(soup.title.string)

        c = soup.select('div.elementor-widget-container')
        contents = c[5]
        for ads in contents.findAll('div', {"class": 'code-block'}):
            ads.decompose()
        for ads in contents.findAll('div', {"align": 'left'}):
            ads.decompose()
        for ads in contents.findAll('div', {"align": 'center'}):
            ads.decompose()
        if contents.h1:
            contents.h1.decompose()
        # end if
        return contents.prettify()
    # end def
# end class
