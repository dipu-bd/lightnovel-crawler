#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
import json
import urllib.parse
from concurrent import futures
from ..utils.crawler import Crawler
from bs4 import BeautifulSoup

logger = logging.getLogger('COMRADEMAO')

#search_url = 'http://novelfull.com/search?keyword=%s'
chapter_list_url = 'https://comrademao.com/wp-admin/admin-ajax.php?action=movie_datatables&p2m=%s&length=%s'


class ComrademaoCrawler(Crawler):
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find('h4').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('div', {'class': 'wrap-thumbnail'}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.find('div', {'class': 'author'}).text.strip()
        logger.info('Novel author: %s', self.novel_author)

        shortlink = soup.find('link', {'rel': 'shortlink'})['href']
        p_id = re.findall(r'p=(\d+)', shortlink)[0]

        response = self.scrapper.post(chapter_list_url % (p_id, 1))
        data = response.json()

        chapter_count = data['recordsTotal']
        response = self.scrapper.post(chapter_list_url % (p_id, chapter_count))
        data = response.json()

        logger.info('Getting chapters...')
        for chapter in reversed(data['data']):
            a = BeautifulSoup(chapter[1], 'lxml').find('a')

            chap_id = len(self.chapters) + 1
            vol_id = (chap_id - 1) // 100 + 1

            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id, 'title': ''})
            # end if

            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': self.absolute_url(a['href']),
                'title': a.text.strip(),
            })
        # end for

        logger.debug(self.chapters)
        logger.debug(self.volumes)

        logger.info('%d volumes and %d chapters found',
                    len(self.volumes), len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        logger.debug(soup.title.string)

        # if soup.select('div.entry-content div.container div.container a p'):
        #    contents = soup.select('div.entry-content div.container div.container a p')
        # else:
        #    contents = soup.select('div.entry-content div.container a p')

        #contents = soup.select('div.entry-content div p')
        #body_parts = []
        # for x in contents:
        #    body_parts.append(x.text)

        # return '<p>' + '</p><p>'.join(body_parts) + '</br></p>'
        #contents = soup.select_one('div.entry-content div')
        if soup.find('div', attrs={'readability': True}):
            contents = soup.find('div', attrs={'readability': True})
        else:
            contents = soup.find('article')
        # end if
        for item in contents.findAll('div'):
            item.decompose()
        # end for
        return contents.prettify()
    # end def
# end class
