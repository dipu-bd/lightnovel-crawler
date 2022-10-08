from typing import Generator

from bs4 import Tag

from ..soup.chapter_only import ChapterOnlySoupTemplate
from .general import GeneralBrowserTemplate


class ChapterOnlyBrowserTemplate(ChapterOnlySoupTemplate, GeneralBrowserTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def parse_chapter_list_in_browser(self) -> None:
        for tag in self.select_chapter_tags_in_browser():
            if not isinstance(tag, Tag):
                continue
            self.process_chapters(tag)

    def select_chapter_tags_in_browser(self) -> Generator[Tag, None, None]:
        """Select chapter list item tags from the browser"""
        return self.select_chapter_tags(self.browser.soup)
