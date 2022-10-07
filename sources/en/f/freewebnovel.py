# -*- coding: utf-8 -*-

from concurrent.futures import Future
from typing import Iterable, List

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate


class FreeWebNovelCrawler(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    base_url = ["https://freewebnovel.com/"]

    def get_search_page_soup(self, query: str) -> BeautifulSoup:
        return self.post_soup(
            f"{self.home_url}search/", data={"searchkey": query.lower()}
        )

    def select_search_items(self, soup: BeautifulSoup) -> Iterable[Tag]:
        return soup.select(".col-content .con .txt h3 a")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        return SearchResult(
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def parse_title(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one(".m-desc h1.tit")
        assert isinstance(tag, Tag), "No title found"
        self.novel_title = tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup):
        tag = soup.select_one(".m-imgtxt img")
        if not isinstance(tag, Tag):
            return
        if tag.has_attr("data-src"):
            self.novel_cover = self.absolute_url(tag["data-src"])
        elif tag.has_attr("src"):
            self.novel_cover = self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup):
        self.novel_author = ", ".join(
            [a.text.strip() for a in soup.select(".m-imgtxt a[href*='/authors/']")]
        )

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

    def parse_chapter_item(self, id: int, a: Tag, soup: BeautifulSoup) -> Chapter:
        return Chapter(
            id=id,
            url=self.absolute_url(a["href"]),
            title=a.text.strip(),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".m-read .txt")
