import logging
from typing import Generator

from bs4 import BeautifulSoup, Tag

from ...core.exeptions import FallbackToBrowser, LNException, ScraperErrorGroup
from ...models import Chapter
from ..soup.general import GeneralSoupTemplate
from .basic import BasicBrowserTemplate

logger = logging.getLogger(__name__)


class GeneralBrowserTemplate(GeneralSoupTemplate, BasicBrowserTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def read_novel_info(self) -> None:
        try:
            return super().read_novel_info()
        except ScraperErrorGroup:
            return self.read_novel_info_in_browser()

    def read_novel_info_in_browser(self) -> None:
        self.visit_novel_page_in_browser()

        try:
            self.novel_title = self.parse_title_in_browser()
        except Exception as e:
            raise FallbackToBrowser() from e

        try:
            self.novel_cover = self.parse_cover_in_browser()
        except Exception as e:
            logger.warn("Failed to parse novel cover | %s", e)

        try:
            authors = set(list(self.parse_authors_in_browser()))
            self.novel_author = ", ".join(authors)
        except Exception as e:
            logger.warn("Failed to parse novel authors | %s", e)

        self.parse_chapter_list_in_browser()

    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        self.visit_chapter_page_in_browser(chapter)
        try:
            body = self.select_chapter_body_in_browser()
            assert body
            return self.parse_chapter_body(body)
        except Exception as e:
            raise LNException("Failed to parse chapter body", e)

    def visit_novel_page_in_browser(self) -> BeautifulSoup:
        """Open the Novel URL in the browser"""
        self.visit(self.novel_url)

    def parse_title_in_browser(self) -> str:
        """Parse and return the novel title in the browser"""
        return self.parse_title(self.browser.soup)

    def parse_cover_in_browser(self) -> str:
        """Parse and return the novel cover image in the browser"""
        return self.parse_cover(self.browser.soup)

    def parse_authors_in_browser(self) -> Generator[Tag, None, None]:
        """Parse and return the novel author in the browser"""
        yield from self.parse_authors(self.browser.soup)

    def parse_chapter_list_in_browser(self) -> None:
        """Parse and return the volumes and chapters in the browser"""
        return self.parse_chapter_list(self.browser.soup)

    def visit_chapter_page_in_browser(self, chapter: Chapter) -> BeautifulSoup:
        """Open the Chapter URL in the browser"""
        self.visit(chapter.url)

    def select_chapter_body_in_browser(self) -> Tag:
        """Select the tag containing the chapter text in the browser"""
        return self.select_chapter_body(self.browser.soup)
