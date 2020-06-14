# -*- coding: utf-8 -*-

import atexit
import json
import logging
from typing import Any, List, Mapping, Union

from bs4 import BeautifulSoup
from requests import Response
from urllib3 import HTTPResponse

from ..config import CONFIG

logger = logging.getLogger(__name__)


class BrowserResponse:

    def __init__(self, resp: Response, url: str, kwargs: dict):
        atexit.register(resp.close)
        self.__url = url
        self.__request = kwargs
        self.__response: Response = resp
        self.__encoding = self.response.encoding or self.response.apparent_encoding

    @property
    def url(self) -> str:
        return self.__url

    def url_args(self) -> Mapping[str, Any]:
        return self.__url_args

    @property
    def response(self) -> Response:
        return self.__response

    @property
    def raw(self) -> HTTPResponse:
        return self.response.raw

    @property
    def encoding(self):
        return self.__encoding

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
    def parser(self) -> str:
        return CONFIG.get('browser/parser')

    @property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(markup=self.text, features=self.parser)
