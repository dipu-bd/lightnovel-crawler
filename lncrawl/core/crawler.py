# -*- coding: utf-8 -*-
"""
Crawler application
"""
import itertools
import logging
import random
import re
import ssl
import sys
import unicodedata
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from urllib.parse import urlparse

import cloudscraper
from bs4 import BeautifulSoup
from bs4.element import Comment, Tag
from requests import Response, Session

from ..assets.user_agents import user_agents
from ..utils.ssl_no_verify import no_ssl_verification

logger = logging.getLogger(__name__)


LINE_SEP = '<br>'

INVISIBLE_CHARS = [c for c in range(sys.maxunicode) if unicodedata.category(chr(c)) in {'Cf', 'Cc'}]
NONPRINTABLE = itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0), INVISIBLE_CHARS)
NONPRINTABLE_MAPPING = {character: None for character in NONPRINTABLE}


class Crawler(ABC):
    '''Blueprint for creating new crawlers'''

    def __init__(self) -> None:
        self._destroyed = False
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Initialize cloudscrapper
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            self.scraper = cloudscraper.create_scraper(
                # debug=True,
                ssl_context=ctx,
                browser={
                    'custom': random.choice(user_agents),
                    #'browser': 'chrome',
                    #'platform': 'windows',
                    #'mobile': False
                }
            )
        except Exception as err:
            logger.exception('Failed to initialize cloudscraper')
            self.scraper = Session()
        # end try

        # Must resolve these fields inside `read_novel_info`
        self.novel_title = ''
        self.novel_author = ''
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

    def initialize(self) -> None:
        pass
    # end def

    def login(self, email: str, password: str) -> None:
        pass
    # end def

    def logout(self) -> None:
        pass
    # end def

    def search_novel(self, query) -> List[Dict[str, str]]:
        '''Gets a list of results matching the given query'''
        return []
    # end def

    @abstractmethod
    def read_novel_info(self) -> None:
        '''Get novel title, autor, cover etc'''
        raise NotImplementedError()
    # end def

    @abstractmethod
    def download_chapter_body(self, chapter) -> str:
        '''Download body of a single chapter and return as clean html format.'''
        raise NotImplementedError()
    # end def

    def download_image(self, url) -> bytes:
        '''Download image from url'''
        logger.info('Downloading image: ' + url)
        response = self.get_response(url, headers={
            'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.9'
        })
        return response.content
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
        if len(url) > 1000 or url.startswith('data:'):
            return url
        # end if
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
            return self.home_url.strip('/') + url
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

    def __process_response(self, response: Response) -> Response:
        if response.status_code == 403 and response.reason == 'Forbidden':
            raise Exception('403 Forbidden! Could not bypass the cloudflare protection.\n'
                            '  If you are running from your own computer, visit the link on your browser and try again later.\n'
                            '  Sometimes, using `http` instead of `https` link may work.')

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
        #headers.setdefault('user-agent', random.choice(user_agents))

        with no_ssl_verification():
            response = self.scraper.get(url, **kargs)

        self.last_visited_url = url.strip('/')
        return self.__process_response(response)
    # end def

    def post_response(self, url, data={}, headers={}) -> Response:
        if self._destroyed:
            raise Exception('Instance is detroyed')
        # end if

        headers = {k.lower(): v for k, v in headers.items()}
        #headers.setdefault('user-agent', random.choice(user_agents))
        headers.setdefault('content-type', 'application/json')
        logger.debug('POST url=%s, data=%s, headers=%s', url, data, headers)

        with no_ssl_verification():
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
        '.code-block', '.adsbygoogle', '.sharedaddy', '.inline-ad-slot', '.ads-middle',
        '.jp-relatedposts', '.ezoic-adpicker-ad', '.ezoic-ad-adaptive', '.ezoic-ad',
        '.cb_p6_patreon_button', 'a[href*="patreon.com"]',
    ]
    p_block_tags = [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'main', 'aside', 'article', 'div', 'section',
    ]
    unchanged_tags = [
        'pre', 'canvas', 'img'
    ]
    plain_text_tags = [
        'span', 'a', 'abbr', 'acronym', 'label', 'time',
    ]
    substitutions = {
        'u003c': '<',
        'u003e': '>',
        '"s': "'s",
        '“s': "'s",
        '”s': "'s",
    }

    def clean_text(self, text) -> str:
        text = str(text).strip()
        text = text.translate(NONPRINTABLE_MAPPING)
        for k, v in self.substitutions.items():
            text = text.replace(k, v)
        return text
    # end def

    def clean_contents(self, div):
        if not isinstance(div, Tag):
            return div
        # end if
        if self.bad_css:
            for bad in div.select(','.join(self.bad_css)):
                bad.extract()
            # end if
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
            elif hasattr(tag, 'attrs'):
                tag.attrs = {k: v for k, v in tag.attrs.items() if k == 'src'}
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
            if not elem.name:
                body.append(self.clean_text(elem))
                continue
            if elem.name in self.unchanged_tags:
                body.append(str(elem))
                continue
            if elem.name == 'hr':
                body.append(LINE_SEP)
                # body.append('-' * 8)
                # body.append(LINE_SEP)
                continue
            if elem.name == 'br':
                body.append(LINE_SEP)
                continue
            # if not elem.text.strip():
            #     continue

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

            if body and body[-1] == LINE_SEP and not is_block:
                body.pop()
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
