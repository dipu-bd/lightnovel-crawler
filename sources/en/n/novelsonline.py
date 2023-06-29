# -*- coding: utf-8 -*-

import logging
from typing import Generator, Union

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, Volume
from lncrawl.templates.browser.general import GeneralBrowserTemplate

logger = logging.getLogger(__name__)


class NovelsOnline(GeneralBrowserTemplate):
    base_url = ["https://novelsonline.net/"]
    has_manga = False
    has_mtl = False

    # TODO: [OPTIONAL] This is called before all other methods.
    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["div"])
        self.cleaner.bad_css.update(
            [
                ".trinity-player-iframe-wrapper",
                ".hidden",
                ".ads-title",
                "script",
                "center",
                "interaction",
                "a[href*=remove-ads]",
                "a[target=_blank]",
                "hr",
                "br",
                "#growfoodsmart",
                ".col-md-6",
                ".trv_player_container",
                ".ad1",
            ]
        )

    # TODO: [OPTIONAL] Open the Novel URL in the browser
    def visit_novel_page_in_browser(self) -> BeautifulSoup:
        self.visit(self.novel_url)
        self.browser.wait(".container--content")

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".block-title h1")
        assert tag
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.find("img", {"alt": self.novel_title})
        assert tag
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        elif tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select("a[href*=author]"):
            yield a.text.strip()

    def parse_chapter_list(
        self, soup: BeautifulSoup
    ) -> Generator[Union[Chapter, Volume], None, None]:
        _id = 0
        for a in soup.select(".chapters .chapter-chs li a"):
            _id += 1
            yield Chapter(
                id=_id, url=self.absolute_url(a["href"]), title=a.text.strip()
            )

    def visit_chapter_page_in_browser(self, chapter: Chapter) -> None:
        self.visit(chapter.url)
        self.browser.wait(".container--content")

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one("#contentall")
