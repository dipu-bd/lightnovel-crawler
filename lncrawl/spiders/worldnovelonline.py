#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [worldnovel.online](https://www.worldnovel.online/).
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from ..utils.crawler import Crawler

logger = logging.getLogger('WORLDNOVEL_ONLINE')
search_url = 'https://www.worldnovel.online/?s=%s'


class WorldnovelonlineCrawler(Crawler):
    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        response = self.get_response(search_url % query)
        soup = BeautifulSoup(response.text, 'lxml')

        results = []
        for a in soup.select('article div h3 a'):
            results.append((
                a.text.strip(),
                self.absolute_url(a['href']),
            ))
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        response = self.get_response(self.novel_url)
        soup = BeautifulSoup(response.content, 'lxml')

        self.novel_title = soup.select_one('h1.elementor-heading-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('div',{'class':'elementor-image'}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.select('div.elementor-shortcode p')[1].findAll('a')
        if len(author)==2:
            self.novel_author = author[0].text + ' (' + author[1].text + ')'
        else :
            self.novel_author = ''
            for a in author:
                self.novel_author = self.novel_author + a.text + ' '
            #end for
        #end if
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
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.content, 'lxml')

        logger.debug(soup.title.string)

        c = soup.select('div.elementor-widget-container')
        contents = c[5]
        for ads in contents.findAll('div',{"class" : 'code-block'}):
            ads.decompose()
        for ads in contents.findAll('div',{"align" : 'left'}):
            ads.decompose()
        for ads in contents.findAll('div',{"align" : 'center'}):
            ads.decompose()
        if contents.h1:
            contents.h1.decompose()
        #end if
        return contents.prettify()
    # end def
# end class
