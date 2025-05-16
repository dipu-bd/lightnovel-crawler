# -*- coding: utf-8 -*-
import logging
from typing import Generator
from urllib.parse import urlencode

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate

logger = logging.getLogger(__name__)


class AsiaNovelNetCrawler(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    base_url = [
        "https://www.asianovel.net/",
        "https://www.wuxiasky.net/"
    ]

    def initialize(self) -> None:
        self.init_executor(ratelimit=1)
        self.cleaner.bad_css.update(
            [
                "div.asian-ads-top-content",
                "div.asian-ads-bottom-content"
            ]
        )

    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        params = {"s": query, "post_type": "fcn_story"}
        soup = self.post_soup(f"{self.home_url}?{urlencode(params)}")
        yield from soup.select("ul#search-result-list > li")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        link = tag.select_one("h3.card__title a")
        chapters = tag.select_one("span.card__footer-chapters")
        tags = tag.select_one("div.card__tag-list")
        info = ""
        if chapters:
            info += f"{chapters.text.strip()} chapters | "
        if tags:
            info += f"Tags: {tags.text.strip()}"
        return SearchResult(
            title=link.text.strip(),
            url=self.absolute_url(link["href"]),
            info=info
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one("div.story__identity h1.story__identity-title")
        assert isinstance(tag, Tag)
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".story__thumbnail a")
        assert isinstance(tag, Tag)
        href = tag.get("href")
        return self.absolute_url(href)

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select("div.story__identity div.story__identity-meta a.author"):
            yield a.text.strip()

    def parse_genres(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select("div.novel-container div#edit-genre a[href*='/genre/']"):
            yield a.text.strip()

    def parse_summary(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one("section.story__summary")
        assert isinstance(tag, Tag)
        related = tag.select_one("div.yarpp-related")
        if isinstance(related, Tag):
            related.extract()
        return tag.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        yield from soup.select("section.story__chapters li > a")

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one("section#chapter-content")
