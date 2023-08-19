# -*- coding: utf-8 -*-
import logging
import re
import js2py
from typing import Generator, Union

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult, Volume
from lncrawl.templates.browser.searchable import SearchableBrowserTemplate
from lncrawl.core.exeptions import FallbackToBrowser

from urllib.parse import urljoin, quote_plus

logger = logging.getLogger(__name__)


digit_regex = re.compile(r"\/(\d+)-")


class RanobeLibCrawler(SearchableBrowserTemplate):
    base_url = [
        "https://ranobes.top/",
        "http://ranobes.top/",
        "https://ranobes.net/",
        "http://ranobes.net/",
    ]
    has_manga = False
    has_mtl = False

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

    def parse_chapter_list_in_browser(
        self,
    ) -> Generator[Union[Chapter, Volume], None, None]:
        self.browser.visit(urljoin(self.home_url, f"/chapters/{self.novel_id}/"))
        self.browser.wait(".chapters__container")
        _pages = max(
            int(a["value"]) for a in self.browser.soup.select(".form_submit option")
        )
        if not _pages:
            _pages = 1
        tags = self.browser.soup.select(".chapters__container .cat_line a")
        for i in range(2, _pages + 1):
            self.browser.visit(
                urljoin(self.home_url, f"/chapters/{self.novel_id}/page/{i}/")
            )
            self.browser.wait(".chapters__container")
            tags += self.browser.soup.select(".chapters__container .cat_line a")

        for _id, _t in enumerate(reversed(tags)):
            yield Chapter(
                id=_id, url=self.absolute_url(_t.get("href")), title=_t.get("title")
            )

    def parse_chapter_list(
        self, soup: BeautifulSoup
    ) -> Generator[Union[Chapter, Volume], None, None]:
        self.novel_id = digit_regex.search(self.novel_url).group(1)
        chapter_list_link = urljoin(self.home_url, f"/chapters/{self.novel_id}/")
        soup = self.get_soup(chapter_list_link)
        script = soup.find(
            lambda tag: isinstance(tag, Tag)
            and tag.name == "script"
            and tag.text.startswith("window.__DATA__")
        )
        assert isinstance(script, Tag)
        data = js2py.eval_js(script.text).to_dict()
        assert isinstance(data, dict)

        pages_count = data["pages_count"]
        logger.info("Total pages: %d", pages_count)

        futures = []
        page_soups = [soup]
        for i in range(2, pages_count + 1):
            chapter_page_url = chapter_list_link.strip("/") + ("/page/%d" % i)
            f = self.executor.submit(self.get_soup, chapter_page_url)
            futures.append(f)
        page_soups += [f.result() for f in futures]

        _i = 0
        for soup in reversed(page_soups):
            script = soup.find(
                lambda tag: isinstance(tag, Tag)
                and tag.name == "script"
                and tag.text.startswith("window.__DATA__")
            )
            assert isinstance(script, Tag)

            data = js2py.eval_js(script.text).to_dict()
            assert isinstance(data, dict)

            for chapter in reversed(data["chapters"]):
                _i += 1
                yield Chapter(
                    id=_i,
                    title=chapter["title"],
                    url=self.absolute_url(chapter["link"]),
                )

    def visit_chapter_page_in_browser(self, chapter: Chapter) -> None:
        self.visit(chapter.url)
        self.browser.wait(".structure")

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        if soup.select_one("div#arrticle"):
            return soup.select_one("div#arrticle")
        else:
            raise FallbackToBrowser
