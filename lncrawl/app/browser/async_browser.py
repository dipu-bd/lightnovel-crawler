# -*- coding: utf-8 -*-

import atexit
import logging
from typing import MutableMapping, Any
from concurrent.futures import Future, ThreadPoolExecutor

from ..config import CONFIG
from .browser import Browser
from .response import BrowserResponse

logger = logging.getLogger(__name__)


class AsyncBrowser:
    def __init__(self, max_workers: int = 20):
        atexit.register(self._close)
        self._browser = Browser()
        self._executor = ThreadPoolExecutor(max_workers)

    def _close(self):
        logger.debug('closing')
        self._executor.shutdown(True)

    def get(self, url: str, **kwargs) -> Future:
        return self._executor.submit(self._browser.get, url, **kwargs)

    def get_sync(self, url: str, **kwargs) -> BrowserResponse:
        return self._browser.get(url, **kwargs)

    def post(self,
             url: str,
             body: MutableMapping[str, Any] = None,
             multipart: bool = False,
             **kwargs) -> Future:
        return self._executor.submit(self._browser.post, url, body, multipart, **kwargs)

    def post_sync(self,
                  url: str,
                  body: MutableMapping[str, Any] = None,
                  multipart: bool = False,
                  **kwargs) -> BrowserResponse:
        return self._browser.post(url, body, multipart, **kwargs)

    def download(self, url: str, filepath: str = None, **kwargs) -> Future:
        return self._executor.submit(self._browser.download, url, filepath, **kwargs)

    def download_sync(self, url: str, filepath: str = None, **kwargs) -> str:
        return self._browser.download(url, filepath, **kwargs)
