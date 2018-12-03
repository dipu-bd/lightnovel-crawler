#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler application
"""
import re
from concurrent import futures
from . import cfscrape


class Crawler:
    '''Blueprint for creating new crawlers'''

    home_url = ''
    novel_url = ''
    last_visited_url = None
    scrapper = cfscrape.create_scraper()
    executor = futures.ThreadPoolExecutor(max_workers=5)

    '''Must resolve these fields inside `read_novel_info`'''
    novel_title = 'N/A'
    novel_author = 'N/A'
    novel_cover = None

    '''
    Each item must contain these keys:
    `id` - 1 based index of the volume
    `title` - the volume title (can be ignored)
    '''
    volumes = []

    '''
    Each item must contain these keys:
    `id` - 1 based index of the chapter
    `title` - the title name
    `volume` - the volume id of this chapter
    `volume_title` - the volume title (can be ignored)
    `url` - the link where to download the chapter
    '''
    chapters = []

    def __init__(self):
        self.scrapper.verify = False
    # end def

    # ------------------------------------------------------------------------- #
    # Implement these methods
    # ------------------------------------------------------------------------- #

    def initialize(self):
        pass
    # end def

    def dispose(self):
        pass
    # end def

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
        '''Return the index of chapter by given url or 0'''
        url = (url or '').strip().strip('/')
        for chapter in self.chapters:
            if chapter['url'] == url:
                return chapter['id']
            # end if
        # end for
        return 0
    # end def

    # ------------------------------------------------------------------------- #
    # Helper methods to be used
    # ------------------------------------------------------------------------- #
    @property
    def headers(self):
        return self.scrapper.headers.copy()
    # end def

    @property
    def cookies(self):
        return {x.name: x.value for x in self.scrapper.cookies}
    # end def

    def absolute_url(self, url, page_url=None):
        url = (url or '').strip()
        page_url = page_url or self.last_visited_url
        if not url or len(url) == 0:
            return None
        elif url.startswith('//'):
            return 'http:' + url
        elif url.find('//') >= 0:
            return url
        elif url.startswith('/'):
            return self.home_url + url
        else:
            return (page_url or self.home_url) + '/' + url
        # end if
    # end def

    def get_response(self, url, incognito=False):
        self.last_visited_url = url.strip('/')
        response = self.scrapper.get(url)
        response.encoding = 'utf-8'
        self.cookies.update({
            x.name: x.value
            for x in response.cookies
        })
        return response
    # end def

    def submit_form(self, url, multipart=False, headers={}, **data):
        '''Submit a form using post request'''
        headers = {
            'content-type': 'multipart/form-data' if multipart
            else 'application/x-www-form-urlencoded'
        }
        response = self.scrapper.post(url, data=data, headers=headers)
        self.cookies.update({
            x.name: x.value
            for x in response.cookies
        })
        return response
    # end def

    def download_cover(self, output_file):
        response = self.get_response(self.novel_cover)
        with open(output_file, 'wb') as f:
            f.write(response.content)
        # end with
    # end def

    blacklist_patterns = [
        r'^[\W\D]*(volume|chapter)[\W\D]+\d+[\W\D]*$',
    ]
    bad_tags = [
        'script', 'iframe', 'form', 'a', 'br', 'ul', 'hr', 'img'
    ]
    block_tags = [
        'h3', 'div', 'p'
    ]

    def is_blacklisted(self, text):
        for pattern in self.blacklist_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
            # end if
        # end for
        return False
    # end def

    def extract_contents(self, contents, level=0):
        body = []
        for elem in contents:
            if self.bad_tags.count(elem.name):
                continue
            elif self.block_tags.count(elem.name):
                body += self.extract_contents(elem.contents, level + 1)
                continue
            # end if
            text = ''
            if not elem.name:
                text = str(elem).strip()
            else:
                text = '<%s>%s</%s>'
                text = text % (elem.name, elem.text.strip(), elem.name)
            # end if
            patterns = [
                re.compile(r'<!--(.|\n)*-->', re.MULTILINE),
                re.compile(r'\[if (.|\n)*!\[endif\]', re.MULTILINE),
            ]
            for x in patterns:
                text = x.sub('', text).strip()
            # end for
            if text:
                body.append(text)
            # end if
        # end for
        if level > 0:
            return body
        # end if

        body = [x for x in body if len(x.strip())]
        length = len(body)
        first_good = 0
        while first_good < length and self.is_blacklisted(body[first_good]):
            first_good += 1
        # end while
        return body[first_good:]
    # end def
# end class
