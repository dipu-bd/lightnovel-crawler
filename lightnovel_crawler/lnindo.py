#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [LnIndo](https://lnindo.org/).
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from .utils.crawler import Crawler

logger = logging.getLogger('LNINDO')


class LnindoCrawler(Crawler):
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        response = self.get_response(self.novel_url)
        soup = BeautifulSoup(response.text, 'lxml')

        self.novel_title = soup.find_all(
            'span', {"typeof": "v:Breadcrumb"})[-1].text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = "https://lnindo.org/images/noavailable.jpg"
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.select('p')[2].text
        self.novel_author = author[20:len(author)-22]
        logger.info('Novel author: %s', self.novel_author)

        #chapters = soup.find('div', {
        #                     'style': '-moz-border-radius: 5px 5px 5px 5px; border: 1px solid #3b5998; color: black; height: 400px; margin: 5px; overflow: auto; padding: 5px; width: 96%;'}).findAll('a')
        #changed due to some change in lnindo site that create text before attribute style so the scrapper that depend on style to detect toc link broken 
        selected = soup.findAll('div')
        for panel in selected :
            if len(panel.attrs)>4:
               toc = panel
        #endfor
        chapters = toc.findAll('a')
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
        soup = BeautifulSoup(response.text, 'lxml')

        for a in soup.find_all('a'):
            a.decompose()

        body_parts = soup.select('p')

        return ''.join([str(p.extract()) for p in body_parts if p.text.strip() and not 'Advertisement' in p.text and not 'JavaScript!' in p.text])
    # end def
# end class
