#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [worldnovel.online](https://www.worldnovel.online/).
"""
import json
import logging
import re
from ..utils.crawler import Crawler
from operator import itemgetter, attrgetter

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

        # score = soup.select_one('span.star')['data-content']

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

        temp_volumes = dict()
        chapter_list = soup.select('div.lightnovel-episode ul li a')
        for a in reversed(chapter_list):
            chap_title = a.text.strip()
            chap_title = chap_title.replace('Bahasa Indonesia', '').strip()

            # loop chapter_list in reverse, otherwise the following two lines won't work
            chap_id = len(self.chapters) + 1
            vol_id = 1 + (chap_id - 1)//100

            try:
                matcher = re.search(r'(book|vol|volume)\s(\d+)', chap_title, re.I)
                if matcher:
                    vol_title = matcher[0]
                    vol_id = int(re.search(r'\d+$', vol_title)[0])
                    temp_volumes[vol_id] = vol_title
                # end if
            except:
                pass # just ignore it
            # end try
            temp_volumes[vol_id] = 'Volume %d' % vol_id

            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': chap_title,
                'url':  self.absolute_url(a['href']),
            })
        # end for

        self.chapters.sort(key=lambda x: x['id'])
        logger.debug(self.chapters)

        self.volumes = [
            {'id': _id, 'title': title}
            for _id, title in sorted(temp_volumes.items())
        ]
        logger.debug(self.volumes)

        logger.debug('%d volumes and %d chapters found',
                     len(self.volumes), len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        logger.debug(soup.title.string)
        # content = soup.find('div',{'data-element_type':'theme-post-content.default'}).soup.select('div.elementor-widget-container')
        contents = soup.find(
            'div', {'data-element_type': 'theme-post-content.default'})
        if contents.findAll('div', {"class": 'code-block'}):
            for ads in contents.findAll('div', {"class": 'code-block'}):
                ads.decompose()
        if contents.findAll('div', {"align": 'left'}):
            for ads in contents.findAll('div', {"align": 'left'}):
                ads.decompose()
        if contents.findAll('div', {"align": 'center'}):
            for ads in contents.findAll('div', {"align": 'center'}):
                ads.decompose()
        # if contents.h1:
        #    contents.h1.decompose()
        # end if
        return contents.prettify()
    # end def
# end class
