# -*- coding: utf-8 -*-

from concurrent.futures import Future
from typing import List

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate


class FreeWebNovelCrawler(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    base_url = ["https://freewebnovel.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h4"])

    def select_search_items(self, query: str):
        data = {"searchkey": query}
        soup = self.post_soup(f"{self.home_url}search/", data=data)
        yield from soup.select(".col-content .con .txt h3 a")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        return SearchResult(
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".m-desc h1.tit")
        assert isinstance(tag, Tag)
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".m-imgtxt img")
        assert isinstance(tag, Tag)
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup):
        for a in soup.select(".m-imgtxt a[href*='/authors/']"):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup):
        pages = soup.select("#indexselect > option")

        futures: List[Future] = []
        for page in pages:
            url = self.absolute_url(page["value"])
            f = self.executor.submit(self.get_soup, url)
            futures.append(f)

        self.resolve_futures(futures, desc="TOC", unit="page")
        for i, future in enumerate(futures):
            assert future.done(), f"Failed to get page {i + 1}"
            soup = future.result()
            yield from soup.select(".m-newest2 li > a")

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            url=self.absolute_url(tag["href"]),
            title=tag.text.strip(),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".m-read .txt")
