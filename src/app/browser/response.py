# -*- coding: utf-8 -*-

import atexit
from concurrent.futures import Future
from threading import Lock
from typing import Union

from bs4 import BeautifulSoup
from requests import Response
from urllib3 import HTTPResponse

from .. import CONFIG


class BrowserResponse:

    def __init__(self, future: Future, timeout: Union[int, float] = 0):
        self.__lock = Lock()
        self.__resolve(future, timeout)

    def __resolve(self, future: Future, timeout: Union[int, float]):
        if timeout is not None and timeout <= 0:
            timeout = CONFIG.browser.response_timeout
        try:
            self.__lock.acquire()
            resp: Response = future.result(timeout)
            resp.raise_for_status()
            self._resp = resp
            atexit.register(self._resp.close)
        except Exception as e:
            self._error = e
        finally:
            self.__lock.release()

    @property
    def response(self) -> Response:
        with self.__lock:
            if hasattr(self, '_resp'):
                return self._resp
            elif hasattr(self, '_error'):
                raise self._error
            else:
                raise ValueError('No response or error')

    @property
    def encoding(self):
        return self.response.apparent_encoding

    @property
    def raw(self) -> HTTPResponse:
        return self.response.raw

    @property
    def content(self) -> bytes:
        return self.response.content

    @property
    def text(self) -> str:
        return self.response.text

    @property
    def json(self) -> dict:
        return self.response.json()

    @property
    def soup(self) -> BeautifulSoup:
        parser: str = CONFIG.browser.soup_parser
        # html = self.content().decode(encoding='utf-8', errors='ignore')
        soup = BeautifulSoup(markup=self.text, features=parser)
        return soup
