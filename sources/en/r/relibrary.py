import logging
from typing import Generator

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate

logger = logging.getLogger(__name__)


class relibCrawler(ChapterOnlySoupTemplate):
    base_url = [
        "https://re-library.com/",
    ]

    def initialize(self) -> None:
        self.init_executor(1)
        self.cleaner.bad_css.update(
            [
                "tr",
                ".nextPageLink",
                ".prevPageLink",
                ".su-button",
                "a[href*='re-library.com']",
            ]
        )
        self.cleaner.bad_tag_text_pairs.update(
            {
                "h2": "References",
            }
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".entry-title")
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".entry-content table img")
        src = tag.get("data-src") or tag.get("src")
        return self.absolute_url(src)

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select_one(".entry-content").select("a[href*='/nauthor/']"):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        yield from soup.select(".page_item > a")

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".entry-content")
