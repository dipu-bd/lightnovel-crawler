from typing import Generator

from bs4 import Tag

from ..soup.with_volume import ChapterWithVolumeSoupTemplate
from .general import GeneralBrowserTemplate


class ChapterWithVolumeBrowserTemplate(
    ChapterWithVolumeSoupTemplate, GeneralBrowserTemplate
):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def parse_chapter_list_in_browser(self) -> None:
        for vol in self.select_volume_tags_in_browser():
            if not isinstance(vol, Tag):
                continue
            self.process_volumes(vol)

    def select_volume_tags_in_browser(self) -> Generator[Tag, None, None]:
        """Select volume list item tags from the browser"""
        return self.select_volume_tags(self.browser.soup)
