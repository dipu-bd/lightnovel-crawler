# -*- coding: utf-8 -*-

import atexit
import json
from concurrent.futures import Future
from threading import Lock
from typing import Union

from bs4 import BeautifulSoup
from requests import Response
from urllib3 import HTTPResponse

from ..config import CONFIG


class BrowserResponse:

    def __init__(self, url: str, future: Future, timeout: Union[int, float] = 0):
        self.__lock = Lock()
        self.__url = url
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
    def url(self) -> str:
        return self.__url

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
        return self.response.encoding or self.response.apparent_encoding

    @property
    def raw(self) -> HTTPResponse:
        return self.response.raw

    @property
    def content(self) -> bytes:
        return self.response.content

    @property
    def text(self) -> str:
        return self.content.decode(
            encoding=self.encoding,
            errors='ignore',
        )

    @property
    def json(self) -> dict:
        try:
            return json.loads(self.text)
        except json.JSONDecodeError:
            return None

    @property
    def soup(self) -> BeautifulSoup:
        parser: str = CONFIG.browser.soup_parser
        soup = BeautifulSoup(markup=self.text, features=parser)
        return soup
