#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [novelonlinefree.info](https://novelonlinefree.info/).
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from ..utils.crawler import Crawler
from math import ceil

logger = logging.getLogger('SCRIBBLEHUB')
search_url = 'https://www.scribblehub.com/?s=%s&post_type=fictionposts'


class ScribbleHubCrawler(Crawler):
    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        response = self.get_response(search_url % query)
        soup = BeautifulSoup(response.text, 'lxml')

        results = []
        for a in soup.select('.search_title a'):
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

        self.novel_title = soup.find('div',{'class':'fic_title'})['title'].strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('div',{'class':'fic_image'}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.find('span',{'class':'auth_name_fic'}).text.strip()
        logger.info('Novel author: %s', self.novel_author)

        chapter_count = soup.find('span',{'class':'cnt_toc'}).text
        chapter_count = -1 if not chapter_count else int(chapter_count)
        page_count = ceil(chapter_count/15)
        logger.info('Chapter list pages: %d' % page_count)
        
        logger.info('Getting chapters...')
        chapters = []
        for i in range(page_count):
            chapters.extend(self.download_chapter_list(i+1))
        # end for

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
                'url': self.absolute_url(x['href']),
                'title': x.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
        logger.debug(self.volumes)
        logger.info('%d volumes and %d chapters found' % (len(self.volumes), len(self.chapters)))
    # end def

    def download_chapter_list(self, page):
        '''Download list of chapters and volumes.'''
        url = self.novel_url.split('?')[0].strip('/')
        url += '?toc=%s#content1' % page
        soup = self.get_soup(url)
        logger.debug('Crawling chapters url in page %s' % page)
        return soup.select('a.toc_a')
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.content, 'lxml')

        logger.debug(soup.title.string)
        contents = soup.find('div', {'id':'chp_contents'})
        #body_parts = []
        #for x in contents:
        #    body_parts.append(x.text)
        #return '<p>' + '</p><p>'.join(body_parts) + '</br></p>'
        return contents.prettify()
    #end def
# end class