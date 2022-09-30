import logging
from typing import Optional, Union

from bs4 import BeautifulSoup
from requests import Response

from .exeptions import LNException

logger = logging.getLogger(__name__)


DEFAULT_PARSER = "lxml"


class SoupMaker:
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

        soup = BeautifulSoup(html, parser or DEFAULT_PARSER)
        if not soup.find("body"):
            raise ConnectionError("HTML document was not loaded properly")

        return soup
