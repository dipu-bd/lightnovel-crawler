import logging
from abc import ABC
from typing import Optional, Union

from bs4 import BeautifulSoup
from requests import Response

from .exeptions import LNException

logger = logging.getLogger(__name__)


DEFAULT_PARSER = "lxml"


class SoupMaker(ABC):
    def __init__(
        self,
        parser: Optional[str] = None,
    ) -> None:
        self.parser = parser or DEFAULT_PARSER

    def __del__(self) -> None:
        pass

    def make_soup(
        self,
        data: Union[Response, bytes, str],
        parser: Optional[str] = None,
    ) -> BeautifulSoup:
        if isinstance(data, Response):
            html = data.content.decode("utf8", "ignore")
        elif isinstance(data, bytes):
            html = data.decode("utf8", "ignore")
        elif isinstance(data, str):
            html = str(data)
        else:
            raise LNException("Could not parse response")
        return BeautifulSoup(html, parser or self.parser)
