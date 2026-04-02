# -*- coding: utf-8 -*-
from typing import Iterable

from lncrawl.core import Novel, PageSoup, SearchResult
from lncrawl.templates.wordpress import WordpressTemplate


class WordRain(WordpressTemplate):
    """Search is broken on the site; novel URL entry still works."""

    base_url = "https://wordrain69.com/"
    can_search = False
    chapter_body_selector = "div.text-left"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(
            [
                "a",
                "h3",
                "script",
            ]
        )
        self.cleaner.bad_css.update(
            [
                ".code-block",
                ".adsbygoogle",
                ".adsense-code",
                ".sharedaddy",
            ]
        )

    def search(self, query: str) -> Iterable[SearchResult]:
        raise NotImplementedError

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:title"]')
        novel.title = tag["content"].rsplit(" ", 1)[0].strip()

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:image"]')
        if tag and tag.get("content"):
            novel.cover_url = self.absolute_url(tag["content"])
        else:
            super().parse_cover(soup, novel)
