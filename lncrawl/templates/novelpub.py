# -*- coding: utf-8 -*-

import logging
import re
from typing import Generator

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.browser.chapter_only import ChapterOnlyBrowserTemplate
from lncrawl.templates.browser.searchable import SearchableBrowserTemplate

logger = logging.getLogger(__name__)

digit_regex = re.compile(r"page[-,=](\d+)")


class NovelPubTemplate(SearchableBrowserTemplate, ChapterOnlyBrowserTemplate):
    def initialize(self) -> None:
        self.init_executor(3)
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
        self.visit(f"{self.home_url}search")
        self.browser.wait("#inputContent")
        inp = self.browser.find("#inputContent")
        inp.send_keys(query)
        self.browser.wait("#novelListBase ul, #novelListBase center")
        soup = self.browser.find("#novelListBase").as_tag()
        yield from soup.select(".novel-list .novel-item a")

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
        title = tag.select_one(".novel-title").text.strip()
        info = [s.text.strip() for s in tag.select(".novel-stats")]
        return SearchResult(
            title=title,
            info=" | ".join(info),
            url=self.absolute_url(tag["href"]),
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one("article#novel .novel-title")
        assert tag
        return tag.text.strip()

    def parse_title_in_browser(self) -> str:
        self.browser.wait("article#novel")
        return self.parse_title(self.browser.soup)

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one("article#novel figure.cover > img")
        assert tag
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.find_all("span", {"itemprop": "author"}):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        chapter_page = f"{self.novel_url.strip('/')}/chapters"
        soup = self.get_soup(chapter_page)
        page_count = max(
            [
                int(digit_regex.search(a["href"]).group(1))
                for a in soup.select(".pagination-container li a[href]")
            ]
        )
        if not page_count:
            page_count = 1

        futures = [self.executor.submit(lambda x: x, soup)]
        futures += [
            self.executor.submit(self.get_soup, f"{chapter_page}/page-{p}")
            for p in range(2, page_count + 1)
        ]
        self.resolve_futures(futures, desc="TOC", unit="page")

        for f in futures:
            soup = f.result()
            yield from soup.select("ul.chapter-list li a")

    def select_chapter_tags_in_browser(self) -> None:
        next_link = f"{self.novel_url.strip('/')}/chapters"
        while next_link:
            self.browser.visit(next_link)
            self.browser.wait("ul.chapter-list li")
            chapter_list = self.browser.find("ul.chapter-list")
            yield from chapter_list.as_tag().select("li a")
            try:
                next_link = self.browser.find('.PagedList-skipToNext a[rel="next"]')
                next_link = next_link.get_attribute("href")
            except Exception:
                next_link = False

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag["title"],
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        self.browser.wait(".chapter-content")
        return soup.select_one(".chapter-content")

    def visit_chapter_page_in_browser(self, chapter: Chapter) -> None:
        """Open the Chapter URL in the browser"""
        self.visit(chapter.url)
        self.browser.wait(".chapter-content", timeout=6)
