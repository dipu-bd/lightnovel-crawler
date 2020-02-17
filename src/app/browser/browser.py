# -*- coding: utf-8 -*-

import atexit
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import *

import cloudscraper

from ..utility import reformat_url
from .response import BrowserResponse

JsonType = Mapping[AnyStr, Any]


class Browser:
    def __init__(self, workers: int = 5):
        # Register cleaner
        atexit.register(self.close)

        # Initialize class variables
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(workers)

        # Initialize internal client
        self.client: cloudscraper.CloudScraper = cloudscraper.create_scraper(
            # Docs: https://github.com/VeNoMouS/cloudscraper
            allow_brotli=False,
            browser=dict(
                browser='firefox',
                desktop=True,
                mobile=False,
            ),
        )

    def close(self):
        self.client.close()
        self.executor.shutdown(True)

    @property
    def cookies(self) -> Mapping[Any, Any]:
        return self.client.cookies.get_dict()

    def get(self, url: str, **kwargs) -> BrowserResponse:
        future = self.executor.submit(self.client.get, url, **kwargs)
        return BrowserResponse(future)

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
        future = self.executor.submit(self.client.post, url, **kwargs)
        return BrowserResponse(future)

    def download_file(self, url: str, filepath: str = None, **kwargs) -> str:
        if filepath is None:
            _, filepath = tempfile.mkstemp()

        chunk_size = 10 * 1024  # TODO: get from Config()

        kwargs['stream'] = True
        res = self.get(url, **kwargs)
        raw = res.raw()

        with open(filepath, 'wb') as f:
            while True:
                chunk = raw.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)

        return filepath
