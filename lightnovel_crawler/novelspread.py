#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from .utils.crawler import Crawler

logger = logging.getLogger('NOVELSPREAD')

book_info_url = 'https://www.novelspread.com/chapter/%s/cover'
menu_url = 'https://www.novelspread.com/api/novel/%s/menu'
chapter_body_url = 'https://www.novelspread.com/chapter/%s'


class NovelSpreadCrawler(Crawler):
    executor = ThreadPoolExecutor(max_workers=1)

    def read_novel_info(self):
        url = self.novel_url
        logger.info('Visiting: %s', url)
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')

        div = soup.select_one('#getNovelId')
        self.novel_id = div['data-novel']
        self.novel_path = div['data-novel_path']
        logger.info('Id: %s', self.novel_id)
        logger.info('Path: %s', self.novel_path)
        
        self.novel_title = soup.select_one('#getNovelId .t-title')['title']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('#getNovelId .novelimg img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = ''
        for div in soup.select('#getNovelId .left-cent .person'):
            self.novel_author += div.find('h3').text.strip()
            self.novel_author += ': '
            self.novel_author += div.find('h4').text.strip()
        # end for
        logger.info('Novel author: %s', self.novel_author)
    # end def

    def download_chapter_list(self):
        '''Download list of chapters and volumes.'''
        url = menu_url % (self.novel_path)
        logger.info('Getting chapter list: %s', url)

        response = self.get_response(url)
        data = response.json()
        logger.debug(data)

        for i, vol in enumerate(data['data']):
            vol_id = i + 1
            vol_title = vol['volume_title']
            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })
            for i, chap in enumerate(vol['chapters']):
                self.chapters.append({
                    'id': i + 1,
                    'hash': chap['id'],
                    'title': chap['title'],
                    'volume': vol_id,
                    'volume_title': vol_title,
                    'url': chapter_body_url % chap['id'],
                    'path': self.absolute_url(chap['path']).strip('/'),
                })
            # end for
        # end for

        logger.debug(self.volumes)
        logger.info('%d volumes found', len(self.volumes))
        logger.debug(self.chapters)
        logger.info('%d chapters found', len(self.chapters))
    # end def

    def get_chapter_index_of(self, url):
        if not url:
            return 0
        url = self.absolute_url(url).strip('/')
        for chap in self.chapters:
            if url == chap['path']:
                return chap['id']
            # end if
        # end for
        return 0
    # end def

    def download_chapter_body(self, chapter):
        url = chapter['url']
        logger.info('Getting chapter... %s [%s]',
                    chapter['title'], chapter['url'])
        
        for i in range(2):
            try:
                response = self.get_response(url)
                data = response.json()
                body = data['data']['chapter_content']
                return body
            except Exception as err:
                logger.debug(err)
                time.sleep(3 + i * 3) # wait to avoid ban
                self.get_response(self.home_url)
                time.sleep(1)
        # end while

        return ''
    # end def
# end class
