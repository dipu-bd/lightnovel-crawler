# -*- coding: utf-8 -*-
from typing import Union

from bs4 import BeautifulSoup
from requests import Response

from .content_type import ContentType
from .request_type import RequestType


class Request:
    def __init__(self,
                 op: RequestType,
                 content: Union[BeautifulSoup, dict, Response]):
        self.op = op
        self.soup: BeautifulSoup = None
        self.json: dict = None
        self.response: Response = None
        if isinstance(content, BeautifulSoup):
            self.soup: BeautifulSoup = content
            self.content_type = ContentType.SOUP
        elif isinstance(content, dict):
            self.json: dict = content
            self.content_type = ContentType.JSON
        elif isinstance(content, Response):
            self.response: Response = content
            self.content_type = ContentType.RESPONSE
        else:
            raise ValueError('Unknown type: ' + type(content))
