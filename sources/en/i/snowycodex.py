# -*- coding: utf-8 -*-

import logging
from typing import Iterable

from bs4 import BeautifulSoup, Tag

from lncrawl.core.exeptions import LNException
from lncrawl.models import Chapter
from lncrawl.templates.soup.single_page import SinglePageSoupTemplate

logger = logging.getLogger(__name__)


class SnowyCodexCrawler(SinglePageSoupTemplate):
    base_url = "https://snowycodex.com/"

    def initialize(self) -> None:
        self.cleaner.bad_css.update([".wpulike"])
        self.cleaner.bad_tags.update(["h2"])

    def parse_title(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one(".entry-content h2")
        if not isinstance(tag, Tag):
            raise LNException("No title found")
        self.novel_title = tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one(".entry-content img")
        if isinstance(tag, Tag):
            if tag.has_attr("data-src"):
                self.novel_cover = self.absolute_url(tag["data-src"])
            elif tag.has_attr("src"):
                self.novel_cover = self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup) -> None:
        tag = soup.find("strong", string="Author:")
        if isinstance(tag, Tag):
            self.novel_author = tag.next_sibling.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup) -> Iterable[Tag]:
        return soup.select(".entry-content a[href*='/chapter']")

    def parse_chapter_item(self, a: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=a.text.strip(),
            url=self.absolute_url(a["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        body = soup.select_one(".entry-content")

        for nav_a in soup.find_all("a", string="Table of Contents"):
            nav_a.parent.extract()

        for img in body.select("img"):
            if img.has_attr("data-src"):
                img.attrs = {"src": img["data-src"]}

        return body
