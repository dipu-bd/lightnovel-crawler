#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for novels from [LNMTL](https://lnmtl.com).
"""
import concurrent.futures
import json
import logging
import re
import sys
from os import path
from shutil import rmtree

import requests
from bs4 import BeautifulSoup

from .interface.crawler import Crawler
from .interface.crawler_app import CrawlerApp

logger = logging.getLogger('LNMTL')
home_url = 'https://lnmtl.com'
login_url = 'https://lnmtl.com/auth/login'
logout_url = 'https://lnmtl.com/auth/logout'


class LNTMLParser:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'lxml')
        self.title = None
    # end def

    def get_title(self):
        try:
            if not self.title:
                SELECTOR = '.novel .media .novel-name'
                self.title = self.soup.select_one(
                    SELECTOR).text.rsplit(' ', 1)[0]
            # end if
        except:
            self.title = 'N/A'
        # end try
        return self.title
    # end def

    def get_login_token(self):
        return self.soup.select_one('form input[name="_token"]')['value']
    # end def

    def has_logout_button(self):
        return self.soup.select_one('a[href="%s"]' % logout_url) is not None
    # end def

    def get_cover(self):
        try:
            title = self.get_title()
            return self.soup.find('img', {'title': title})['src']
        except:
            return ''
        # end try
    # end def

    def get_volumes(self):
        for script in self.soup.find_all('script'):
            text = script.text.strip()
            if not text.startswith('window.lnmtl'):
                continue
            # end if
            i, j = text.find('lnmtl.volumes = '), text.find(';lnmtl.route')
            if i <= 0 and j <= i:
                continue
            # end if
            i += len('lnmtl.volumes =')
            return json.loads(text[i:j].strip())
        # end for
        return []
    # end def

    def get_chapter_body(self):
        body = self.soup.select('.chapter-body .translated')
        body = [self.format_text(x.text) for x in body if x]
        body = '\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])
        return body
    # end def

    def format_text(self, text):
        '''formats the text and remove bad characters'''
        text = text.replace(u'\u00ad', '')
        text = re.sub(r'\u201e[, ]*', '&ldquo;', text)
        text = re.sub(r'\u201d[, ]*', '&rdquo;', text)
        text = re.sub(r'[ ]*,[ ]+', ', ', text)
        return text.strip()
    # end def

    def display_body(self):
        logger.debug('-' * 80)
        body = self.soup.select_one('body').text
        logger.debug('\n\n'.join(
            [x for x in body.split('\n\n') if len(x.strip())]))
        logger.debug('-' * 80)
    # end def
# end class


class LNTMLCrawler(Crawler):
    @property
    def supports_login(self):
        return True
    # end def

    def login(self, email, password):
        '''login to LNMTL'''
        # Get the login page
        logger.debug('Visiting %s', login_url)
        response = self.get_response(login_url)
        self.headers['cookie'] = '; '.join(
            [x.name + '=' + x.value for x in response.cookies])
        # Send post request to login
        parser = LNTMLParser(response.text)
        logger.debug('Logging in...')
        response = self.submit_form(
            login_url,
            email=email,
            password=password,
            _token=parser.get_login_token(),
        )
        # Update the cookies
        self.headers['cookie'] = '; '.join(
            [x.name + '=' + x.value for x in response.cookies])
        # Check if logged in successfully
        if LNTMLParser(response.text).has_logout_button():
            logger.warning('Logged in')
        else:
            parser = LNMTLCrawlerApp(response.text)
            parser.display_body()
            logger.warning('Failed to login')
        # end if
    # end def

    def logout(self):
        '''logout as a good citizen'''
        logger.debug('Logging out...')
        response = self.get_response(logout_url)
        if LNTMLParser(response.text).has_logout_button():
            logger.warning('Failed to logout.')
        else:
            logger.warning('Logged out.')
        # end if
    # end def

    def read_novel_info(self, url):
        '''get list of chapters'''
        logger.debug('Visiting %s', url)
        response = self.get_response(url)
        parser = LNTMLParser(response.text)
        self.novel_title = parser.get_title()
        self.novel_cover = parser.get_cover()
        self.volumes = [
            {'id': vol['id'], 'title': vol['title']}
            for vol in parser.get_volumes()
        ]
        logger.debug(self.volumes)
        logger.warning('%d volumes found. Loading chapters...',
                       len(self.volumes))
        self.download_chapter_list()
    # end def

    def download_chapter(self, chapter):
        logger.debug('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        parser = LNTMLParser(response.text)
        body = parser.get_chapter_body()
        return '<h1>%s</h1><h2>%s</h1>\n%s' % (
            chapter['name'], chapter['title'], body)
    # end def

    def download_chapter_list(self):
        self.chapters = []
        page_url = '%s/chapter?page=1' % home_url
        future_to_url = {
            self.executor.submit(
                self.download_chapter_list_of_volume,
                index,
                page_url
            ): index
            for index in range(len(self.volumes))
        }
        for future in concurrent.futures.as_completed(future_to_url):
            concurrent.futures.wait(future.result())
        # end for
        self.chapters = sorted(self.chapters, key=lambda x: int(x['id']))
        logger.debug(self.chapters)
        logger.warning('[%s] %d chapters found',
                       self.novel_title, len(self.chapters))
    # end def

    def download_chapter_list_of_volume(self, vol_index, page_url):
        vol_id = self.volumes[vol_index]['id']
        url = '%s&volumeId=%s' % (page_url, vol_id)
        logger.debug('Visiting %s', url)
        result = self.get_response(url).json()
        page_url = result['next_page_url']
        for chapter in result['data']:
            special = '(Special)' if chapter['is_special'] == '1' else ''
            chapter_name = 'Chapter #%s%s' % (chapter['number'], special)
            self.chapters.append({
                'id': int(chapter['position']),
                'name': chapter_name,
                'title': chapter['title'],
                'url': chapter['site_url'],
                'volume': self.volumes[vol_index]['title'],
            })
        # end for
        if result['current_page'] == 1:
            return {
                self.executor.submit(
                    self.download_chapter_list_of_volume,
                    vol_index,
                    '%s/chapter?page=%s' % (home_url, page + 1)
                ): '%s-%s' % (vol_id, page)
                for page in range(1, result['last_page'])
            }
        # end if
        return {}
    # end def
# end class


class LNMTLCrawlerApp(CrawlerApp):
    crawler = LNTMLCrawler()
# end class


if __name__ == '__main__':
    LNMTLCrawlerApp().start()
# end if
