import logging
from typing import Generator

from bs4 import BeautifulSoup, Tag
from time import sleep

from lncrawl.models import Chapter
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate

logger = logging.getLogger(__name__)


class relibCrawler(ChapterOnlySoupTemplate):
    base_url = ["https://re-library.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                ".nextPageLink",
                ".prevPageLink",
                ".su-button",
                "a[href*='re-library.com']",
            ]
        )
        self.cleaner.bad_tag_text_pairs.update({"h2": "References"})

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".entry-title")
        assert tag
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".entry-content table img")
        assert tag
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select_one(".entry-content").select("a[href*='/nauthor/']"):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        yield from soup.select(".page_item > a ")

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        sleep(5)
        tag = soup.select_one(".entry-content")
        assert tag
        return tag
