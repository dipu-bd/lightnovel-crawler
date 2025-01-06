# -*- coding: utf-8 -*-
import logging
import re
import json
from typing import Generator

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.browser.searchable import SearchableBrowserTemplate

from urllib.parse import urljoin, quote_plus

logger = logging.getLogger(__name__)


digit_regex = re.compile(r"\/(\d+)-")


class RanobeLibCrawler(SearchableBrowserTemplate):
    base_url = [
        "https://ranobes.top/",
        "https://ranobes.net/",
    ]

    def initialize(self) -> None:
        self.cleaner.bad_css.update([".free-support", 'div[id^="adfox_"]'])

    def select_search_items_in_browser(self, query: str) -> Generator[Tag, None, None]:
        self.visit(urljoin(self.home_url, "/search/{}/".format(quote_plus(query))))
        self.browser.wait(".breadcrumbs-panel")
        for elem in self.browser.select(".short-cont .title a"):
            yield elem

    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        soup = self.get_soup(
            urljoin(self.home_url, "/search/{}/".format(quote_plus(query)))
        )

        for elem in soup.select(".short-cont .title a"):
            yield elem

    def parse_search_item(self, tag: Tag) -> SearchResult:
        return SearchResult(
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def visit_novel_page_in_browser(self) -> BeautifulSoup:
        self.visit(self.novel_url)
        self.browser.wait(".body_left_in")
        self.novel_id = digit_regex.search(self.novel_url).group(1)

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one("h1.title")
        assert tag
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".r-fullstory-poster .poster a img")
        assert tag
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select('.tag_list a[href*="/authors/"]'):
            yield a.text.strip()

    def parse_chapter_list_in_browser(self) -> Generator[Chapter, None, None]:
        self.browser._driver.implicitly_wait(1)
        self.browser.click('a[href^="/chapters/"][title="Go to table of contents"]')

        index = 0
        while True:
            self.browser.wait(".cat_line a")
            for tag in self.browser.find_all(".cat_line a"):
                index += 1
                yield Chapter(
                    id=index,
                    title=tag.get_attribute("title"),
                    url=self.absolute_url(tag.get_attribute("href")),
                )

            next_page = self.browser.find(".page_next a")
            if not next_page:
                break
            self.browser._driver.implicitly_wait(1)
            next_page.scroll_into_view()
            next_page.click()

    def parse_chapter_list(self, soup: BeautifulSoup) -> Generator[Chapter, None, None]:
        self.novel_id = digit_regex.search(self.novel_url).group(1)
        chapter_list_link = urljoin(self.home_url, f"/chapters/{self.novel_id}/")
        soup = self.get_soup(chapter_list_link)

        data = self.extract_page_data(soup)
        pages_count = data["pages_count"]
        logger.info("Total pages: %d", pages_count)

        futures = []
        page_soups = [soup]
        for i in range(2, pages_count + 1):
            chapter_page_url = chapter_list_link.strip("/") + ("/page/%d" % i)
            futures.append(self.executor.submit(self.get_soup, chapter_page_url))
        page_soups += [f.result() for f in futures]

        index = 0
        for soup in enumerate(reversed(page_soups)):
            data = self.extract_page_data(soup)
            for chapter in reversed(data["chapters"]):
                index += 1
                yield Chapter(
                    id=index,
                    title=chapter["title"],
                    url=self.absolute_url(chapter["link"]),
                )

    def visit_chapter_page_in_browser(self, chapter: Chapter) -> None:
        self.visit(chapter.url)
        self.browser.wait("#arrticle")

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one("div#arrticle")

    def extract_page_data(self, soup: BeautifulSoup) -> dict:
        script = soup.find(
            lambda tag: isinstance(tag, Tag)
            and tag.name == "script"
            and tag.text.startswith("window.__DATA__")
        )
        assert isinstance(script, Tag)

        content = script.text.strip()
        content = content.replace("window.__DATA__ = ", "")

        data = json.loads(content)
        return data
