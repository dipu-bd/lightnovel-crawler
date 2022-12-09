from typing import Generator

from bs4 import Tag

from ...models import Chapter
from ..soup.chapter_only import ChapterOnlySoupTemplate
from .general import GeneralBrowserTemplate


class ChapterOnlyBrowserTemplate(GeneralBrowserTemplate, ChapterOnlySoupTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def parse_chapter_list_in_browser(self) -> Generator[Chapter, None, None]:
        chap_id = 0
        for tag in self.select_chapter_tags_in_browser():
            if not isinstance(tag, Tag):
                continue
            chap_id += 1
            yield self.parse_chapter_item(tag, chap_id)

    def select_chapter_tags_in_browser(self) -> Generator[Tag, None, None]:
        """Select chapter list item tags from the browser"""
        yield from self.select_chapter_tags(self.browser.soup)
