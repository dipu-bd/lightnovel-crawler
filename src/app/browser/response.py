# -*- coding: utf-8 -*-

import atexit
from concurrent.futures import Future

from bs4 import BeautifulSoup
from requests import Response
from urllib3 import HTTPResponse


class BrowserResponse:

    def __init__(self, furure: Future):
        atexit.register(self.close)
        self.count = 0
        self.total = 0
        self._future = furure

    def close(self):
        if hasattr(self, '_closed'):
            return
        setattr(self, '_closed', True)
        if hasattr(self, '_resp'):
            getattr(self, '_resp').close()

    def response(self, timeout: float = None) -> Response:
        # Return from cache if available
        if hasattr(self, '_resp'):
            return getattr(self, '_resp')
        # Wait for future to finish
        resp: Response = self._future.result(timeout)
        resp.raise_for_status()
        # Update cache
        setattr(self, '_resp', resp)
        return resp

    def raw(self) -> HTTPResponse:
        return self.response().raw

    def content(self) -> bytes:
        return self.response().content

    def text(self) -> str:
        return self.response().text

    def json(self, **kwargs):
        return self.response().json(**kwargs)

    def soup(self, parser: str = 'html5lib') -> BeautifulSoup:
        # TODO: use Config() to get parser
        html = self.content().decode(encoding='utf-8', errors='ignore')
        soup = BeautifulSoup(markup=self.text(), features=parser)
        return soup
