#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for novels from [LNMTL](https://lnmtl.com).
"""
import json
import logging
import re
from concurrent import futures

import requests

from .app.crawler import Crawler
from .app.crawler_app import CrawlerApp
from .app.parser import Parser

LOGGER = logging.getLogger('LNMTL')

home_url = 'https://lnmtl.com'
login_url = 'https://lnmtl.com/auth/login'
logout_url = 'https://lnmtl.com/auth/logout'


class LNTMLParser(Parser):
    def get_login_token(self):
        return self.soup.select_one('form input[name="_token"]')['value']
    # end def

    def has_logout_button(self):
        return self.soup.select_one('a[href="%s"]' % logout_url) is not None
    # end def

    def get_title(self):
        try:
            SELECTOR = '.novel .media .novel-name'
            return self.soup.select_one(SELECTOR).text.rsplit(' ', 1)[0]
        except:
            return 'N/A'
        # end try
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
        return body.strip()
    # end def

    def format_text(self, text):
        '''formats the text and remove bad characters'''
        text = text.replace(u'\u00ad', '')
        text = re.sub(r'\u201e[, ]*', '&ldquo;', text)
        text = re.sub(r'\u201d[, ]*', '&rdquo;', text)
        text = re.sub(r'[ ]*,[ ]+', ', ', text)
        return text.strip()
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
        LOGGER.info('Visiting %s', login_url)
        response = self.get_response(login_url)
        parser = LNTMLParser(response.text)
        # Send post request to login
        LOGGER.info('Logging in...')
        response = self.submit_form(
            login_url,
            email=email,
            password=password,
            _token=parser.get_login_token(),
        )
        # Check if logged in successfully
        parser = LNTMLParser(response.text)
        if parser.has_logout_button():
            LOGGER.warning('Logged in')
        else:
            parser.print_body()
            LOGGER.error('Failed to login')
        # end if
    # end def

    def logout(self):
        '''logout as a good citizen'''
        LOGGER.debug('Logging out...')
        response = self.get_response(logout_url)
        parser = LNTMLParser(response.text)
        if parser.has_logout_button():
            LOGGER.error('Failed to logout.')
        else:
            LOGGER.warning('Logged out.')
        # end if
    # end def

    def read_novel_info(self, url):
        '''get list of chapters'''
        LOGGER.info('Visiting %s', url)
        response = self.get_response(url)
        parser = LNTMLParser(response.text)
        self.novel_title = parser.get_title()
        LOGGER.info('Novel title = %s', self.novel_title)
        self.novel_cover = parser.get_cover()
        LOGGER.info('Novel cover = %s', self.novel_cover)
        self.volumes = []
        for i, vol in enumerate(parser.get_volumes()):
            title = re.sub(r'[^\u0000-\u00FF]', '', vol['title'])
            title = re.sub(r'\(\)', '', title).strip()
            mdash = ' - ' if len(title) > 0 else ''
            title = 'Volume %d%s%s' % (i + 1, mdash, title)
            self.volumes.append({
                'id': vol['id'],
                'title': title,
            })
        # end for
        LOGGER.debug(self.volumes)
        LOGGER.info('%d volumes found.', len(self.volumes))
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
        for future in futures.as_completed(future_to_url):
            futures.wait(future.result())
        # end for
        self.chapters = sorted(self.chapters, key=lambda x: int(x['id']))
        LOGGER.debug(self.chapters)
        LOGGER.info('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_list_of_volume(self, vol_index, page_url):
        vol_id = self.volumes[vol_index]['id']
        url = '%s&volumeId=%s' % (page_url, vol_id)
        LOGGER.info('Visiting %s', url)
        result = self.get_response(url).json()
        page_url = result['next_page_url']
        for chapter in result['data']:
            title = 'Chapter #%s - %s' % (chapter['position'], chapter['title'])
            self.chapters.append({
                'id': int(chapter['position']),
                'title': title,
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

    def download_chapter_body(self, url):
        LOGGER.info('Downloading %s', url)
        response = self.get_response(url)
        parser = LNTMLParser(response.text)
        return parser.get_chapter_body()
    # end def
# end class


class LNMTLCrawlerApp(CrawlerApp):
    crawler = LNTMLCrawler()
# end class


if __name__ == '__main__':
    LNMTLCrawlerApp().start()
# end if
