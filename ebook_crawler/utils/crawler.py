#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler application
"""
from concurrent import futures
import cfscrape
import requests


class Crawler:
    '''Blueprint for creating new crawlers'''

    executor = futures.ThreadPoolExecutor(max_workers=5)

    cookies = {}
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    '''Must resolve these fields inside `read_novel_info`'''
    novel_title = 'N/A'
    novel_author = 'N/A'
    novel_cover = None
    scrapper = None

    '''
    Each item must contain these keys:
    `title` - the title of the volume
    '''
    volumes = []

    '''
    Each item must contain these keys:
    `id` - the index of the chapter
    `title` - the title name
    `volume` - the volume id of this chapter
    `url` - the link where to download the chapter
    `name` - the chapter name, e.g: 'Chapter 3' or 'Chapter 12 (Special)'
    '''
    chapters = []

    # ------------------------------------------------------------------------- #
    # Implement these methods
    # ------------------------------------------------------------------------- #

    @property
    def supports_login(self):
        '''Whether the crawler supports login() and logout method'''
        return False
    # end def

    def login(self, email, password):
        pass
    # end def

    def logout(self):
        pass
    # end def

    def read_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        pass
    # end def

    def download_chapter_list(self):
        '''Download list of chapters and volumes.'''
        pass
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        pass
    # end def

    def get_chapter_index_of(self, url):
        '''Return the index of chapter by given url or -1'''
        url = (url or '').strip(' /')
        for i, chapter in enumerate(self.chapters):
            if chapter['url'] == url:
                return i
            # end if
        # end for
        return -1
    # end def

    # ------------------------------------------------------------------------- #
    # Helper methods to be used
    # ------------------------------------------------------------------------- #
    def get_response_cf(self, url, incognito=False):
        if self.scrapper==None:
            self.scrapper = cfscrape.create_scraper()
        response = self.scrapper.get(url)
        return response
    # end def

    def get_response(self, url, incognito=False):
        response = requests.get(
            url,
            headers=self._build_headers(),
            verify=False, # whether to verify ssl certs for https
        )
        self.cookies.update({
            x.name: x.value
            for x in response.cookies
        })
        return response
    # end def

    def submit_form(self, url, multipart=False, headers={}, **data):
        '''Submit a form using post request'''
        headers = self._build_headers({
            'content-type': 'multipart/form-data' if multipart \
                else 'application/x-www-form-urlencoded'
        })
        response = requests.post(
            url,
            data=data,
            headers=headers,
            verify=False, # whether to verify ssl certs for https
        )
        self.cookies.update({
            x.name: x.value
            for x in response.cookies
        })
        return response
    # end def

    def _build_headers(self, headers={}):
        headers = self.headers.copy()
        headers['cookie'] = '; '.join([
            '%s=%s' % (x, self.cookies[x])
            for x in self.cookies
        ])
        headers.update(headers or {})
        return headers
    # end def

# end class
