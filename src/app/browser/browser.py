# -*- coding: utf-8 -*-

import atexit
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import Any, MutableMapping, Union

from requests import Session
from requests.adapters import HTTPAdapter
from cloudscraper import CloudScraper, create_scraper
from requests.cookies import RequestsCookieJar

from ..config import CONFIG
from .response import BrowserResponse


class Browser(object):

    def __new__(cls, *args, **kwargs):
        instance = super(Browser, cls).__new__(cls, *args, **kwargs)
        atexit.register(instance.__exit__)
        return instance

    def __init__(self, workers: int = 5, engine: str = None):
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(workers)
        self.load_engine(engine)

    def __exit__(self):
        if hasattr(self, 'client'):
            self.client.close()
        if hasattr(self, 'executor'):
            self.executor.shutdown(True)

    def load_engine(self, engine: str = None):
        if not isinstance(engine, str):
            engine = CONFIG.browser.engine

        if engine == 'requests':
            self.client: Session = Session()
        elif engine == 'cloudscraper':
            cs_config = CONFIG.browser.cloudscraper
            self.client: CloudScraper = create_scraper(**cs_config)
            # self.client.get_adapter('https://').ssl_context.check_hostname = False
        # TODO: add support for firefox, chrome, safari web engines
        else:
            raise NameError('Unrecognized web-engine: %s' % engine)

    @property
    def cookies(self) -> Union[RequestsCookieJar, MutableMapping[str, str]]:
        return self.client.cookies

    def get(self, url: str, **kwargs) -> BrowserResponse:
        timeout = kwargs.get('timeout', None)
        future = self.executor.submit(self.client.get, url, **kwargs)
        return BrowserResponse(future, timeout)

    def post(self,
             url,
             body: MutableMapping[str, Any] = None,
             multipart: bool = False,
             **kwargs) -> BrowserResponse:
        if not body:
            body = {}

        headers: dict = kwargs.get('headers', {})
        if multipart:
            headers['Content-Type'] = 'multipart/form-data'
        elif 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

        kwargs['data'] = body
        kwargs['headers'] = headers
        timeout = kwargs.get('timeout', None)
        future = self.executor.submit(self.client.post, url, **kwargs)
        return BrowserResponse(future, timeout)

    def download(self, url: str, filepath: str = None, **kwargs) -> str:
        if filepath is None:
            _, filepath = tempfile.mkstemp()

        kwargs['stream'] = True
        res = self.get(url, **kwargs)
        raw = res.raw()

        chunk_size = CONFIG.browser.stream_chunk_size

        with open(filepath, 'wb') as f:
            while True:
                chunk = raw.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)

        return filepath
