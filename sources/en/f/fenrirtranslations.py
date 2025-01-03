# -*- coding: utf-8 -*-
import logging
from typing import Generator
from urllib.parse import urlencode, quote_plus

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate

logger = logging.getLogger(__name__)


class FenrirTranslationsCrawler(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    base_url = ["https://fenrirtranslations.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                "div.chapter-warning",
                "div.code-block"
            ]
        )

    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        params = {"s": quote_plus(query.lower()), "post_type": "wp-manga"}
        soup = self.post_soup(f"{self.home_url}?{urlencode(params)}")
        yield from soup.select(".post-title a[href*='/series/']")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        return SearchResult(
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".tab-summary .post-content .post-title")
        assert isinstance(tag, Tag)
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".tab-summary .summary_image img")
        assert isinstance(tag, Tag)
        src = tag.get("src")
        return self.absolute_url(src)

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select(".tab-summary .post-content .manga-authors a[href*='/author/']"):
            yield a.text.strip()

    def parse_genres(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select(".tab-summary .post-content a[href*='/genre/']"):
            yield a.text.strip()

    def parse_summary(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".tab-summary .post-content div.manga-summary")
        assert isinstance(tag, Tag)
        return tag.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        novel_url_without_slash = self.novel_url.rstrip("/")
        headers = {
            "Accept": "*/*",
            "Referer": self.novel_url,
            "X-Requested-With": "XMLHttpRequest"
        }
        chapters_soup = self.post_soup(f"{novel_url_without_slash}/ajax/chapters/", headers=headers)
        yield from reversed(chapters_soup.select("section.free li.free-chap a"))

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".entry-content .reading-content")
