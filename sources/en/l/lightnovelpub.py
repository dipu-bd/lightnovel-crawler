# -*- coding: utf-8 -*-

import logging
from typing import Generator

from re import search

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.browser.chapter_only import ChapterOnlyBrowserTemplate
from lncrawl.templates.browser.searchable import SearchableBrowserTemplate

logger = logging.getLogger(__name__)


class LightNovelPubCrawler(SearchableBrowserTemplate, ChapterOnlyBrowserTemplate):
    base_url = [
        "https://www.lightnovelpub.com/",
        "https://www.lightnovelworld.com/",
        "https://www.novelpub.com/",
    ]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["div"])
        self.cleaner.bad_css.update(
            [
                ".adsbox",
                ".ad-container",
                "p > strong > strong",
                ".OUTBRAIN",
                "p[class]",
                ".ad",
                "p:nth-child(1) > strong",
                ".noveltopads",
                ".chadsticky",
            ]
        )

    def select_search_items_in_browser(self, query: str) -> Generator[Tag, None, None]:
        pass

    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        soup = self.get_soup(f"{self.home_url}search")
        token_tag = soup.select_one(
            '#novelSearchForm input[name="__LNRequestVerifyToken"]'
        )
        assert token_tag, "No request verify token found"
        token = token_tag["value"]

        response = self.submit_form(
            f"{self.home_url}lnsearchlive",
            data={"inputContent": query},
            headers={
                "lnrequestverifytoken": token,
                "referer": f"{self.home_url}search",
            },
        )

        soup = self.make_soup(response.json()["resultview"])
        yield from soup.select(".novel-list .novel-item a")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        return SearchResult(
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def parse_chapter_list_in_browser(self) -> None:
        max_page = 1
        self.visit(f"{self.novel_url}/chapters")
        soup = self.browser.soup.select(".pagination-container li a")
        if len(soup) > 0:
            max_page = int(search("-([1-9]*)$", soup[-1]["href"]).group(1))

        for p in [
            f"{self.novel_url}/chapters/page-{p}" for p in range(1, max_page + 1)
        ]:
            self.visit(p)
            for tag in self.select_chapter_tags_in_browser():
                if not isinstance(tag, Tag):
                    continue
                self.process_chapters(tag)

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        yield from soup.select("ul.chapter-list li a")

    def parse_chapter_list(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        max_page = 1
        soup = self.get_soup(f"{self.novel_url}/chapters").select(
            ".pagination-container li a"
        )
        if len(soup) > 0:
            max_page = int(search("-([1-9]*)$", soup[-1]["href"]).group(1))

        for p in [
            f"{self.novel_url}/chapters/page-{p}" for p in range(1, max_page + 1)
        ]:
            for tag in self.select_chapter_tags(self.get_soup(p)):
                if not isinstance(tag, Tag):
                    continue
                self.process_chapters(tag)

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".novel-title")
        assert tag
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".cover > img")
        assert tag
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.findAll("span", {"itemprop": "author"}):
            yield a.text.strip()

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".chapter-content")
