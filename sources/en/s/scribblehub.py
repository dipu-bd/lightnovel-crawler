# -*- coding: utf-8 -*-

import logging
import re
from typing import Generator, Union
from urllib.parse import urljoin

from lncrawl.core import Chapter, PageSoup, SearchResult, Volume
from lncrawl.exceptions import FallbackToBrowser, LNException
from lncrawl.templates.browser.searchable import SearchableBrowserTemplate

logger = logging.getLogger(__name__)

digit_regex = re.compile(r"\?toc=(\d+)#content1$")


class ScribbleHubCrawler(SearchableBrowserTemplate):
    base_url = "https://www.scribblehub.com/"
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

    def select_search_items_in_browser(self, query: str) -> Generator[PageSoup, None, None]:
        raise LNException("Browser Search not supported")

    def select_search_items(self, query: str) -> Generator[PageSoup, None, None]:
        raise FallbackToBrowser()

    def parse_search_item(self, tag: PageSoup) -> SearchResult:
        return SearchResult(
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def visit_novel_page_in_browser(self) -> PageSoup:
        url_parts = self.novel_url.split("/")
        self.novel_url = f"{url_parts[0]}/{url_parts[2]}/{url_parts[3]}/{url_parts[4]}/"
        logger.debug(self.novel_url)
        self.visit(self.novel_url)
        self.browser.wait(".fictionposts-template-default")

    def parse_title(self, soup: PageSoup) -> str:
        tag = soup.select_one(".fic_title")
        assert tag, "No title found"
        return tag.text.strip()

    def parse_cover(self, soup: PageSoup) -> str:
        tag = soup.select_one(".fic_image img")
        if not tag:
            return
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: PageSoup) -> Generator[str, None, None]:
        for a in soup.select(".auth_name_fic"):
            yield a.text.strip()

    def parse_genres(self, soup: PageSoup) -> Generator[str, None, None]:
        for a in soup.select("a.fic_genre"):
            yield a.text.strip()

    def parse_summary(self, soup: PageSoup) -> str:
        tag = soup.select_one(".wi_fic_desc")
        return self.cleaner.extract_contents(tag)

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
            yield Chapter(id=_id, url=self.absolute_url(_t.get("href")), title=_t.text.strip())

    def parse_chapter_list(self, soup: PageSoup) -> Generator[Union[Chapter, Volume], None, None]:
        chapter_count = soup.find("span", {"class": "cnt_toc"})
        chapter_count = int(chapter_count.text) if chapter_count else -1

        possible_mypostid = soup.select_one("input#mypostid")
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
        self.browser.wait("main#main")

    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        return soup.select_one("#chp_raw")
