# -*- coding: utf-8 -*-
"""
Crawler application
"""
import logging
import random
import ssl
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore
from typing import Dict, List
from urllib.parse import urlparse

import cloudscraper
from bs4 import BeautifulSoup
from requests import Response, Session
from requests.exceptions import ProxyError, RequestException

from ..assets.user_agents import user_agents
from ..utils.cleaner import TextCleaner
from ..utils.ssl_no_verify import no_ssl_verification
from .exeptions import LNException
from .proxy import get_a_proxy, remove_faulty_proxies

logger = logging.getLogger(__name__)

MAX_WORKER_COUNT = 10
MAX_CONCURRENT_REQUEST_PER_DOMAIN = 25
REQUEST_SEMAPHORES: Dict[str, Semaphore] = {}


def get_domain_semaphore(url):
    host = urlparse(url).hostname or url
    if host not in REQUEST_SEMAPHORES:
        REQUEST_SEMAPHORES[host] = Semaphore(MAX_CONCURRENT_REQUEST_PER_DOMAIN)
    return REQUEST_SEMAPHORES[host]


class Crawler(ABC):
    '''Blueprint for creating new crawlers'''

    # ------------------------------------------------------------------------- #
    # Internal methods
    # ------------------------------------------------------------------------- #
    def __init__(self) -> None:
        self._destroyed = False
        self.cleaner = TextCleaner()
        self.executor = ThreadPoolExecutor(MAX_WORKER_COUNT)

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

        # Setup an automatic proxy switcher
        self.enable_auto_proxy = False
    # end def

    def __generate_proxy(self, url, **kwargs):
        if not self.enable_auto_proxy or not url:
            return None
        # end if
        scheme = urlparse(self.home_url).scheme
        return { scheme: get_a_proxy(scheme,  **kwargs) }
    # end def

    def __process_request(self, method: str, url, **kwargs):
        method_call = getattr(self.scraper, method)
        assert callable(method_call), f'No request method: {method}'
        
        kwargs = kwargs or dict()
        retry = kwargs.pop('retry', 2)
        #kwargs.setdefault('verify', False)
        #kwargs.setdefault('allow_redirects', True)
        headers = kwargs.setdefault('headers', {})
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault('host', urlparse(self.home_url).hostname)
        headers.setdefault('origin', self.home_url.strip('/'))
        headers.setdefault('referer', self.novel_url.strip('/'))
        kwargs['proxies'] = self.__generate_proxy(url)

        while retry >= 0:
            if self._destroyed:
                raise LNException('Instance is detroyed')
            # end if
            try:
                logger.debug('[%s] %s\n%s', method.upper(), url, 
                    ', '.join([f'{k}={v}' for k, v in kwargs.items()]))

                with get_domain_semaphore(url):
                    with no_ssl_verification():
                        response: Response = method_call(url, **kwargs)
                
                response.raise_for_status()
                response.encoding = 'utf8'
                self.cookies.update({
                    x.name: x.value
                    for x in response.cookies
                })
                return response
            except RequestException as e:
                if retry == 0: # retry attempt depleted
                    raise e
                # end if
                logger.debug('%s | Retrying...', e)
                retry -= 1
                if isinstance(e, ProxyError):
                    for proxy_url in kwargs.get('proxies', {}).values():
                        remove_faulty_proxies(proxy_url)
                    # end for
                # end if
                if retry != 0: # do not use proxy on last attemp
                    kwargs['proxies'] = self.__generate_proxy(url, timeout=2)
                # end if
            # end try
        # end while
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
    
    def set_cookie(self, name: str, value: str) -> None:
        self.scraper.cookies[name] = value
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

    def get_response(self, url, **kwargs) -> Response:
        kwargs = kwargs or dict()
        kwargs.setdefault('retry', 5)
        kwargs.setdefault('timeout', (7, 301))  # in seconds

        result = self.__process_request('get', url, **kwargs)
        self.last_visited_url = url.strip('/')
        return result
    # end def

    def post_response(self, url, data={}, headers={}, **kwargs) -> Response:
        kwargs = kwargs or dict()
        kwargs.setdefault('retry', 2)
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault('content-type', 'application/json')
        kwargs['headers'] = headers
        kwargs['data'] = data

        return self.__process_request('get', url, **kwargs)
    # end def

    def submit_form(self, url, data={}, multipart=False, headers={}) -> Response:
        '''Submit a form using post request'''
        if self._destroyed:
            raise LNException('Instance is detroyed')
        # end if
 
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault('content-type', 'multipart/form-data' if multipart \
            else 'application/x-www-form-urlencoded; charset=UTF-8')
        headers.setdefault('host', urlparse(self.home_url).hostname)
        headers.setdefault('origin', self.home_url.strip('/'))
        headers.setdefault('referer', self.novel_url.strip('/'))

        return self.post_response(url, data, headers)
    # end def

    def get_soup(self, url, **kwargs) -> BeautifulSoup:
        '''Downloads an URL and make a BeautifulSoup object from response'''
        parser = kwargs.pop('parser', None)
        response = self.get_response(url, **kwargs)
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
            raise LNException('Could not parse response')
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
        headers.setdefault('accept', 'application/json, text/plain, */*')
        response = self.post_response(url, data, headers)
        return response.json()
    # end def

    def download_cover(self, output_file) -> None:
        response = self.get_response(self.novel_cover)
        with open(output_file, 'wb') as f:
            f.write(response.content)
        # end with
    # end def
    
# end class
