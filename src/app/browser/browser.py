# -*- coding: utf-8 -*-

import atexit
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import *

from cloudscraper import CloudScraper, create_scraper

from ..utility import reformat_url
from .response import BrowserResponse

from .. import CONFIG


class Browser(object):
    def __new__(cls, *args, **kwargs):
        instance = super(Browser, cls).__new__(cls, *args, **kwargs)
        atexit.register(instance.__exit__)
        return instance

    def __init__(self, workers: int = 5):
        # Initialize class variables
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(workers)

        # Initialize internal client
        cs_config = CONFIG.browser.cloudscraper
        self.client: CloudScraper = create_scraper(**cs_config)

    def __exit__(self):
        if hasattr(self, 'client'):
            self.client.close()
        if hasattr(self, 'executor'):
            self.executor.shutdown(True)

    @property
    def cookies(self) -> Mapping[Any, Any]:
        return self.client.cookies.get_dict()

    def get(self, url: str, **kwargs) -> BrowserResponse:
        timeout = kwargs.get('timeout', None)
        future = self.executor.submit(self.client.get, url, **kwargs)
        return BrowserResponse(future, timeout)

    def post(self, url, body: Mapping[str, Any] = None, multipart: bool = False, **kwargs) -> BrowserResponse:
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
