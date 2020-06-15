# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, List, Mapping, Union

from requests import Response
from urllib3 import HTTPResponse

from ..config import CONFIG
from .soup_ex import ExtendedSoup

logger = logging.getLogger(__name__)


class BrowserResponse:

    def __init__(self, url: str, resp: Response):
        self.__url = url
        self.__response: Response = resp
        self.__encoding = resp.encoding or resp.apparent_encoding
        self.parser: str = CONFIG.get('browser/parser')

    @property
    def url(self) -> str:
        return self.__url

    @property
    def response(self) -> Response:
        return self.__response

    @property
    def encoding(self) -> str:
        return self.__encoding

    @property
    def content(self) -> bytes:
        return self.response.content

    @property
    def text(self) -> str:
        if not hasattr(self, '__text'):
            self.__text = self.content.decode(encoding=self.encoding, errors='ignore')
        return self.__text

    @property
    def json(self) -> dict:
        if not hasattr(self, '__json'):
            try:
                self.__json = json.loads(self.text)
            except json.JSONDecodeError:
                self.__json = {}
        return self.__json

    @property
    def soup(self) -> ExtendedSoup:
        if not hasattr(self, '__soup'):
            self.__soup = ExtendedSoup(markup=self.text, features=self.parser)
        return self.__soup
