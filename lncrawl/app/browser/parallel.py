# -*- coding: utf-8 -*-

import atexit
import logging
from concurrent.futures import Future, ThreadPoolExecutor

from ..config import CONFIG
from .response import Browser

logger = logging.getLogger(__name__)


class ParallelBrowser:
    def __init__(self, scraper_id: str):
        atexit.register(self._close)
        self._browser = Browser()
        self._config = CONFIG.default('concurrency/per_crawler', scraper_id)
        self._executor = ThreadPoolExecutor(self._config.get('workers', 20))

    def _close(self):
        logger.debug('closing')
        self._executor.shutdown(True)

    def get(self, url: str, **kwargs) -> Future[BrowserResponse]:
        return self._executor.submit(self._browser.get(url, **kwargs))

    def get_sync(self, url: str, **kwargs) -> BrowserResponse:
        return self._browser.get(url, **kwargs)

    def post(self,
             url: str,
             body: MutableMapping[str, Any] = None,
             multipart: bool = False,
             **kwargs) -> Future[BrowserResponse]:
        return self._executor.submit(self._browser.post(url, body, multipart, **kwargs))

    def post(self,
             url: str,
             body: MutableMapping[str, Any] = None,
             multipart: bool = False,
             **kwargs) -> BrowserResponse:
        return self._browser.post(url, body, multipart, **kwargs)

    def download(self, url: str, filepath: str = None, **kwargs) -> Future[str]:
        return self._executor.submit(self._browser.download(url, filepath, **kwargs))

    def download_sync(self, url: str, filepath: str = None, **kwargs) -> str:
        return self._browser.download(url, filepath, **kwargs)
