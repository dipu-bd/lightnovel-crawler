import logging
from abc import ABC
from typing import Optional, Union

from bs4 import BeautifulSoup, Tag
from requests import Response

from .exeptions import LNException

logger = logging.getLogger(__name__)


DEFAULT_PARSER = "lxml"


class SoupMaker(ABC):
    def __init__(
        self,
        parser: Optional[str] = None,
    ) -> None:
        """This is a helper for Beautiful Soup. It is being used as a superclass of the Crawler.

        Args:
        - parser (Optional[str], optional): Desirable features of the parser. This can be the name of a specific parser
            ("lxml", "lxml-xml", "html.parser", or "html5lib") or it may be the type of markup to be used ("html", "html5", "xml").
        """
        self._parser = parser or DEFAULT_PARSER

    def __del__(self) -> None:
        pass

    def make_soup(
        self,
        data: Union[Response, bytes, str],
        encoding: Optional[str] = None,
    ) -> BeautifulSoup:
        if isinstance(data, Response):
            return self.make_soup(data.content, encoding)
        elif isinstance(data, bytes):
            html = data.decode(encoding or "utf8", "ignore")
        elif isinstance(data, str):
            html = data
        else:
            raise LNException("Could not parse response")
        return BeautifulSoup(html, features=self._parser)

    def make_tag(
        self,
        data: Union[Response, bytes, str],
        encoding: Optional[str] = None,
    ) -> Tag:
        soup = self.make_soup(data, encoding)
        return next(soup.find("body").children)
