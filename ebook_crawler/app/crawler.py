#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler application
"""
import requests
from concurrent import futures

class Crawler:
    '''Blueprint for creating new crawlers'''

    executor = futures.ThreadPoolExecutor(max_workers=5)

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    '''Must resolve these fields inside `read_novel_info`'''
    novel_title = 'N/A'
    novel_author = 'N/A'
    novel_cover = None

    '''
    Each item must contain these keys:
    `title` - the title of the volume
    '''
    volumes = []

    '''
    Each item must contain these keys:
    `id` - the position of the chapter
    `title` - the title name
    `volume` - the volume title
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
        '''Login and update cookies in `headers`'''
        pass
    # end def

    def logout(self):
        '''Logout and update cookies in `headers`'''
        pass
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover, volumes and chapters'''
        pass
    # end def

    def download_chapter(self, url):
        '''Download body of a single chapter and return as clean html format.'''
        pass
    # end def

    # ------------------------------------------------------------------------- #
    # Helper methods to be used
    # ------------------------------------------------------------------------- #

    def get_response(self, url):
        return requests.get(
            url,
            headers=self.headers,
            verify=False # whether to verify ssl certs for https
        )
    # end def

    def submit_form(self, url, **data):
        headers = self.headers.copy()
        headers['content-type'] = 'application/x-www-form-urlencoded'
        return requests.post(
            url,
            data=data,
            headers=headers,
            verify=False # whether to verify ssl certs for https
        )
    # end def
# end class
