#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
import logging
from concurrent import futures
from ..utils.crawler import Crawler

logger = logging.getLogger('COMRADEMAO')
#search_url = 'http://novelfull.com/search?keyword=%s'


class ComrademaoCrawler(Crawler):

    #temp_chapters = []

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find('h4').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(soup.find('div',{'class':'wrap-thumbnail'}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.find('div',{'class':'author'}).text.strip()
        logger.info('Novel author: %s', self.novel_author)

        page_count = soup.find('span',{'class':'dots'}).findNext('a').text
        page_count = -1 if not page_count else int(page_count)
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
        url += '/page/%s/' % page
        soup = self.get_soup(url)
        logger.debug('Crawling chapters url in page %s' % page)
        return soup.select('tbody td a')
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.content, 'lxml')
        logger.debug(soup.title.string)
        
        if soup.select('div.entry-content div.container div.container a p'):
            contents = soup.select('div.entry-content div.container div.container a p')
        else:
            contents = soup.select('div.entry-content div.container a p')
            
        body_parts = []
        for x in contents:
            body_parts.append(x.text)
        #body = self.extract_contents(body_parts)
        return '<p>' + '</p><p>'.join(body_parts) + '</br></p>'
        #body = self.extract_contents(soup.select('div.entry-content div.container a p'))
        #return '<p>' + '</p><p>'.join(body) + '</p>'
        #return contents
    # end def
# end class
