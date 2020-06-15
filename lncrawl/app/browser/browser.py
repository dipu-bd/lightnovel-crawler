# -*- coding: utf-8 -*-

import atexit
import logging
import tempfile
from typing import Any, MutableMapping

from cloudscraper import CloudScraper, create_scraper

from ..config import CONFIG
from .response import BrowserResponse
from .scheduler import ConnectionControl

__all__ = [
    'Browser'
]

logger = logging.getLogger(__name__)


class Browser:
    def __init__(self):
        atexit.register(self.close)
        config = CONFIG.get('browser/cloudscraper', {})
        self.client: CloudScraper = create_scraper(**config)

    @property
    def stream_chunk_size(self) -> int:
        return CONFIG.get('browser/stream_chunk_size')

    def close(self):
        logger.debug('closing')
        self.client.close()

    def get(self, url: str, **kwargs) -> BrowserResponse:
        with ConnectionControl(url):
            resp = self.client.get(url, **kwargs)
            resp.raise_for_status()
            return BrowserResponse(url, resp)

    def post(self,
             url: str,
             body: MutableMapping[str, Any] = None,
             multipart: bool = False,
             **kwargs) -> BrowserResponse:
        with ConnectionControl(url):
            body = kwargs.setdefault('body', {})
            headers = kwargs.setdefault('headers', {})

            if multipart:
                headers['Content-Type'] = 'multipart/form-data'
            elif 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

            resp = self.client.post(url, **kwargs)
            resp.raise_for_status()
            return BrowserResponse(url, resp)

    def download(self, url: str, filepath: str = None, **kwargs) -> str:
        with ConnectionControl(url):
            kwargs['stream'] = True
            res = self.get(url, **kwargs)
            raw = res.raw()

            if filepath is None:
                _, filepath = tempfile.mkstemp()

            with open(filepath, 'wb') as f:
                while True:
                    chunk = raw.read(self.stream_chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
            return filepath
