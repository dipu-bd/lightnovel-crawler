# -*- coding: utf-8 -*-

import logging
import re

from typing import Generator, Union

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult, Volume
from lncrawl.templates.browser.searchable import SearchableBrowserTemplate
from lncrawl.core.exeptions import FallbackToBrowser, LNException

#from urllib.parse import urljoin, quote_plus
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

digit_regex = re.compile(r"\?toc=(\d+)#content1$")


class ScribbleHubCrawler(SearchableBrowserTemplate):
    base_url = [
        "https://www.scribblehub.com/",
        "https://scribblehub.com/",
    ]

    has_manga = False
    has_mtl = False

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                ".p-avatar-wrap",
                ".sp-head",
                ".spdiv",
                ".chp_stats_feature",
                ".modern-footnotes-footnote",
                ".modern-footnotes-footnote__note",
                ".wi_authornotes",
            ]
        )
        self.cleaner.whitelist_attributes.update(
            [
                "border",
                "class",
            ]
        )
        self.cleaner.whitelist_css_property.update(
            [
                "text-align",
            ]
        )

    def select_search_items_in_browser(self, query: str) -> Generator[Tag, None, None]:
        # self.visit(
        #     urljoin(
        #         self.home_url, "/?s={}&post_type=fictionposts".format(quote_plus(query))
        #     )
        # )
        # self.browser.wait(".search")
        # for elem in self.browser.soup.select(
        #     ".fic .search_main_box .search_body .search_title a"
        # ):
        #     yield elem
        raise LNException('Browser Search not supported')

    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        raise FallbackToBrowser()

    def parse_search_item(self, tag: Tag) -> SearchResult:
        return SearchResult(
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def visit_novel_page_in_browser(self) -> BeautifulSoup:
        url_parts = self.novel_url.split("/")
        self.novel_url = f'{url_parts[0]}/{url_parts[2]}/{url_parts[3]}/{url_parts[4]}/'
        logger.debug(self.novel_url)
        self.visit(self.novel_url)
        self.browser.wait(".fictionposts-template-default")

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".fic_title")
        assert tag
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".fic_image img")
        assert tag
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        elif tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select(".nauth_name_fic"):
            yield a.text.strip()

    def parse_chapter_list_in_browser(
        self,
    ) -> Generator[Union[Chapter, Volume], None, None]:
        _pages = max(
            [
                int(digit_regex.search(a["href"]).group(1))
                for a in self.browser.soup.select(".simple-pagination a")
                if digit_regex.search(a["href"]) is not None
            ]
        )
        if not _pages:
            _pages = 1
        tags = self.browser.soup.select(".main .toc li a")
        for i in range(2, _pages + 1):
            self.browser.visit(urljoin(self.novel_url, f"?toc={i}#content1"))
            self.browser.wait(".main")
            tags += self.browser.soup.select(".main .toc li a")

        for _id, _t in enumerate(reversed(tags)):
            yield Chapter(
                id=_id, url=self.absolute_url(_t.get("href")), title=_t.text.strip()
            )

    def parse_chapter_list(
        self, soup: BeautifulSoup
    ) -> Generator[Union[Chapter, Volume], None, None]:
        chapter_count = soup.find("span", {"class": "cnt_toc"})
        chapter_count = (
            int(chapter_count.text) if isinstance(chapter_count, Tag) else -1
        )

        possible_mypostid = soup.select_one("input#mypostid")
        assert isinstance(possible_mypostid, Tag)
        mypostid = int(str(possible_mypostid["value"]))
        logger.info("#mypostid = %d", mypostid)

        response = self.submit_form(
            f"{self.home_url}wp-admin/admin-ajax.php",
            {
                "action": "wi_getreleases_pagination",
                "pagenum": -1,
                "mypostid": mypostid,
            },
        )
        soup = self.make_soup(response)
        for chapter in reversed(soup.select(".toc_ol a.toc_a")):
            yield Chapter(
                id=len(self.chapters) + 1,
                url=self.absolute_url(str(chapter["href"])),
                title=chapter.text.strip(),
            )

    def visit_chapter_page_in_browser(self, chapter: Chapter) -> None:
        self.visit(chapter.url)
        self.browser.wait(".site-content-contain")

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one("div#chp_raw")
