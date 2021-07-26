# -*- coding: utf-8 -*-
"""
Crawler application
"""
import logging
import re
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import cloudscraper
from bs4 import BeautifulSoup
from bs4.element import Comment
from requests import Response, Session

logger = logging.getLogger(__name__)

_default_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'

LINE_SEP = '<br>'


class Crawler:
    '''Blueprint for creating new crawlers'''

    def __init__(self) -> None:
        self._destroyed = False
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Initialize cloudscrapper
        try:
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'platform': 'linux',
                    'mobile': False
                }
            )
        except Exception as err:
            logger.exception('Failed to initialize cloudscraper')
            self.scraper = Session()
        # end try

        # Must resolve these fields inside `read_novel_info`
        self.novel_title = 'N/A'
        self.novel_author = 'N/A'
        self.novel_cover = None
        self.is_rtl = False

        # Each item must contain these keys:
        # `id` - 1 based index of the volume
        # `title` - the volume title (can be ignored)
        self.volumes = []

        # Each item must contain these keys:
        # `id` - 1 based index of the chapter
        # `title` - the title name
        # `volume` - the volume id of this chapter
        # `volume_title` - the volume title (can be ignored)
        # `url` - the link where to download the chapter
        self.chapters = []

        # Other stuffs - not necessary to resolve from crawler instance.
        self.home_url = ''
        self.novel_url = ''
        self.last_visited_url = None
    # end def

    # ------------------------------------------------------------------------- #
    # Implement these methods
    # ------------------------------------------------------------------------- #

    @abstractmethod
    def initialize(self) -> None:
        pass
    # end def

    @abstractmethod
    def login(self, email: str, password: str) -> None:
        pass
    # end def

    @abstractmethod
    def logout(self) -> None:
        pass
    # end def

    @abstractmethod
    def search_novel(self, query):
        '''Gets a list of results matching the given query'''
        pass
    # end def

    @abstractmethod
    def read_novel_info(self) -> None:
        '''Get novel title, autor, cover etc'''
        pass
    # end def

    @abstractmethod
    def download_chapter_body(self, chapter) -> str:
        '''Download body of a single chapter and return as clean html format.'''
        pass
    # end def

    def get_chapter_index_of(self, url) -> int:
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

    def destroy(self) -> None:
        self._destroyed = True
        self.volumes.clear()
        self.chapters.clear()
        self.scraper.close()
        self.executor.shutdown(False)
    # end def

    @property
    def headers(self) -> dict:
        return dict(self.scraper.headers)
    # end def

    def set_header(self, key: str, value: str) -> None:
        self.scraper.headers[key.lower()] = value
    # end def

    @property
    def cookies(self) -> dict:
        return {x.name: x.value for x in self.scraper.cookies}
    # end def

    def absolute_url(self, url, page_url=None) -> str:
        url = (url or '').strip()
        if not page_url:
            page_url = self.last_visited_url
        # end if
        if not url or len(url) == 0:
            return url
        elif url.startswith('//'):
            return self.home_url.split(':')[0] + ':' + url
        elif url.find('//') >= 0:
            return url
        elif url.startswith('/'):
            return self.home_url + url
        elif page_url:
            return page_url.strip('/') + '/' + url
        else:
            return self.home_url + url
        # end if
    # end def

    def is_relative_url(self, url) -> bool:
        page = urlparse(self.novel_url)
        url = urlparse(url)
        return (page.hostname == url.hostname
                and url.path.startswith(page.path))
    # end def

    def __process_response(self, response) -> Response:
        response.raise_for_status()
        response.encoding = 'utf8'
        self.cookies.update({
            x.name: x.value
            for x in response.cookies
        })
        return response

    def get_response(self, url, **kargs) -> Response:
        if self._destroyed:
            raise Exception('Instance is detroyed')
        # end if

        kargs = kargs or dict()
        #kargs.setdefault('verify', False)
        #kargs.setdefault('allow_redirects', True)
        kargs.setdefault('timeout', 150)  # in seconds
        headers = kargs.setdefault('headers', {})

        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault('user-agent', _default_user_agent)

        response: Response = self.scraper.get(url, **kargs)
        self.last_visited_url = url.strip('/')
        return self.__process_response(response)
    # end def

    def post_response(self, url, data={}, headers={}) -> Response:
        if self._destroyed:
            raise Exception('Instance is detroyed')
        # end if

        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault('user-agent', _default_user_agent)
        headers.setdefault('content-type', 'application/json')
        logger.debug('POST url=%s, data=%s, headers=%s', url, data, headers)

        response = self.scraper.post(
            url,
            data=data,
            headers=headers,
            # verify=False,
            # allow_redirects=True,
        )
        return self.__process_response(response)
    # end def

    def submit_form(self, url, data={}, multipart=False, headers={}) -> Response:
        '''Submit a form using post request'''
        if self._destroyed:
            raise Exception('Instance is detroyed')
        # end if

        content_type = 'application/x-www-form-urlencoded; charset=UTF-8'
        if multipart:
            content_type = 'multipart/form-data'
        # end if
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault('content-type', content_type)

        response = self.post_response(url, data, headers)
        return self.__process_response(response)
    # end def

    def get_soup(self, *args, **kwargs) -> BeautifulSoup:
        parser = kwargs.pop('parser', None)
        response = self.get_response(*args, **kwargs)
        return self.make_soup(response, parser)
    # end def

    def make_soup(self, response, parser=None) -> BeautifulSoup:
        if isinstance(response, Response):
            html = response.content.decode('utf8', 'ignore')
        elif isinstance(response, bytes):
            html = response.decode('utf8', 'ignore')
        elif isinstance(response, str):
            html = str(response)
        else:
            raise Exception('Could not parse response')
        # end if
        soup = BeautifulSoup(html, parser or 'lxml')
        if not soup.find('body'):
            raise ConnectionError('HTML document was not loaded properly')
        # end if
        return soup
    # end def

    def get_json(self, *args, **kwargs) -> dict:
        kwargs = kwargs or dict()
        headers = kwargs.setdefault('headers', {})
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault('accept', 'application/json, text/javascript, */*')
        response = self.get_response(*args, **kwargs)
        return response.json()
    # end def

    def post_soup(self, url, data={}, headers={}, parser='lxml') -> BeautifulSoup:
        response = self.post_response(url, data, headers)
        return self.make_soup(response, parser)
    # end def

    def post_json(self, url, data={}, headers={}) -> dict:
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault('accept', 'application/json, text/javascript, */*')
        response = self.post_response(url, data, headers)
        return response.json()
    # end def

    def download_cover(self, output_file) -> None:
        response = self.get_response(self.novel_cover)
        with open(output_file, 'wb') as f:
            f.write(response.content)
        # end with
    # end def

    # ------------------------------------------------------------------------- #

    blacklist_patterns = []
    bad_tags = [
        'noscript', 'script', 'style', 'iframe', 'ins', 'header', 'footer',
        'button', 'input', 'amp-auto-ads', 'pirate', 'figcaption', 'address',
        'tfoot', 'object', 'video', 'audio', 'source', 'nav', 'output', 'select',
        'textarea', 'form', 'map',
    ]
    bad_css = [
        '.code-block', '.adsbygoogle', '.sharedaddy'
    ]
    p_block_tags = [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'main', 'aside', 'article', 'div', 'section',
    ]
    unchanged_tags = [
        None, '', 'pre', 'canvas',
    ]
    plain_text_tags = [
        'span', 'a', 'abbr', 'acronym', 'label', 'time',
    ]

    def clean_contents(self, div):
        if not div:
            return div
        # end if
        for bad in div.select(','.join(self.bad_css)):
            bad.extract()
        # end if
        for tag in div.find_all(True):
            if isinstance(tag, Comment):
                tag.extract()   # Remove comments
            elif tag.name == 'br':
                next_tag = getattr(tag, 'next_sibling')
                if next_tag and getattr(next_tag, 'name') == 'br':
                    tag.extract()
                # end if
            elif tag.name in self.bad_tags:
                tag.extract()   # Remove bad tags
            elif hasattr(tag, 'attrs') and tag != 'img':
                tag.attrs = {}  # Remove attributes
            # end if
        # end for
        div.attrs = {}
        return div
    # end def

    def extract_contents(self, tag) -> str:
        self.clean_contents(tag)
        body = ' '.join(self.__extract_contents(tag))
        return '\n'.join([
            '<p>' + x + '</p>'
            for x in body.split(LINE_SEP)
            if not self.__is_in_blacklist(x.strip())
        ])
    # end def

    def __extract_contents(self, tag) -> list:
        body = []
        for elem in tag.contents:
            if isinstance(elem, Comment):
                continue
            elif elem.name in self.unchanged_tags:
                body.append(str(elem).strip())
                continue
            # end if
            text = elem.text.strip()
            if elem.name == 'hr':
                body.append(LINE_SEP)
                body.append('-' * 8)
                body.append(LINE_SEP)
            elif elem.name == 'br':
                body.append(LINE_SEP)
            elif text:
                is_block = elem.name in self.p_block_tags
                is_plain = elem.name in self.plain_text_tags
                content = ' '.join(self.__extract_contents(elem))
                if is_block:
                    body.append(LINE_SEP)
                # end if
                for line in content.split(LINE_SEP):
                    line = line.strip()
                    if not line:
                        continue
                    # end if
                    if not (is_plain or is_block):
                        line = '<%s>%s</%s>' % (elem.name, line, elem.name)
                    # end if
                    body.append(line)
                    body.append(LINE_SEP)
                # end if
                if not is_block:
                    body.pop()
                # end if
            # end if
        # end for
        return [x.strip() for x in body if x.strip()]
    # end def

    def __is_in_blacklist(self, text) -> bool:
        if not text:
            return True
        # end if
        if not self.blacklist_patterns:
            return False
        # end if
        pattern = getattr(self, '__blacklist__', None)
        if not pattern:
            pattern = re.compile('|'.join(['(%s)' % p for p in self.blacklist_patterns]))
            setattr(self, '__blacklist__', pattern)
        # end if
        if pattern and pattern.search(text):
            return True
        return False
    # end def

# end class
