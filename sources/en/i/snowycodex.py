# -*- coding: utf-8 -*-

import logging
from typing import Generator

from lncrawl.core import Chapter, PageSoup
from lncrawl.templates.browser.chapter_only import ChapterOnlyBrowserTemplate

logger = logging.getLogger(__name__)


class SnowyCodexCrawler(ChapterOnlyBrowserTemplate):
    base_url = "https://snowycodex.com/"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            {
                ".wpulike",
                ".sharedaddy",
                ".wpulike-default",
                '[style="text-align:center;"]',
            }
        )
        self.cleaner.bad_tag_text_pairs.update(
            {
                "p": r"[\u4E00-\u9FFF]+",
            }
        )

    def parse_title(self, soup: PageSoup) -> str:
        tag = soup.select_one(".entry-content h2")
        return tag.text.strip()

    def parse_cover(self, soup: PageSoup) -> str:
        tag = soup.select_one(".entry-content img")
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        elif tag.has_attr("src"):
            return self.absolute_url(tag["src"])
        return ""

    def parse_authors(self, soup: PageSoup) -> Generator[str, None, None]:
        tag = soup.find("strong", string="Author:")  # type: ignore
        if tag:
            next = tag.find_next_sibling()
            if next:
                yield next.get_text(strip=True)

    def select_chapter_tags(self, soup: PageSoup):
        yield from soup.select(".entry-content a[href*='/chapter']")

    def parse_chapter_item(self, tag: PageSoup, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        return soup.select_one(".entry-content")
