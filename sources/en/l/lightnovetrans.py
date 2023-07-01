# -*- coding: utf-8 -*-

import logging
from typing import Generator, Union

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, Volume
from lncrawl.templates.soup.general import GeneralSoupTemplate

logger = logging.getLogger(__name__)


class LNTCrawler(GeneralSoupTemplate):
    base_url = ["https://lightnovelstranslations.com/"]

    has_manga = False
    has_mtl = False

    def get_novel_soup(self) -> BeautifulSoup:
        return self.get_soup(f"{self.novel_url}/?tab=table_contents")

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".novel_title")
        assert tag
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".novel-image img")
        assert tag
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for p in soup.select(".entry-content > p"):
            if "Author" in p.text:
                yield p.text.replace("Author:", "").strip()

    def parse_chapter_list(
        self, soup: BeautifulSoup
    ) -> Generator[Union[Chapter, Volume], None, None]:
        _id = 0
        for a in soup.select(".novel_list_chapter_content li.unlock a"):
            _id += 1
            yield Chapter(
                id=_id, url=self.absolute_url(a["href"]), title=a.text.strip()
            )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".text_story")
