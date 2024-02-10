import logging
from typing import Generator, Union

from bs4 import BeautifulSoup, Tag

from ...core.exeptions import FallbackToBrowser
from ...models import Chapter, Volume
from ..soup.general import GeneralSoupTemplate
from .basic import BasicBrowserTemplate

logger = logging.getLogger(__name__)


class GeneralBrowserTemplate(BasicBrowserTemplate, GeneralSoupTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def read_novel_info_in_scraper(self) -> None:
        soup = self.get_novel_soup()

        try:
            self.novel_title = self.parse_title(soup)
        except Exception as e:
            raise FallbackToBrowser() from e

        try:
            self.novel_cover = self.parse_cover(soup)
        except Exception as e:
            logger.warning("Failed to parse novel cover | %s", e)

        try:
            authors = set(list(self.parse_authors(soup)))
            self.novel_author = ", ".join(authors)
        except Exception as e:
            logger.warning("Failed to parse novel authors | %s", e)

        for item in self.parse_chapter_list(soup):
            if isinstance(item, Chapter):
                self.chapters.append(item)
            elif isinstance(item, Volume):
                self.volumes.append(item)

    def visit_novel_page_in_browser(self) -> BeautifulSoup:
        """Open the Novel URL in the browser"""
        self.visit(self.novel_url)

    def read_novel_info_in_browser(self) -> None:
        self.visit_novel_page_in_browser()

        self.novel_title = self.parse_title_in_browser()

        try:
            self.novel_cover = self.parse_cover_in_browser()
        except Exception as e:
            logger.warning("Failed to parse novel cover | %s", e)

        try:
            authors = set(list(self.parse_authors_in_browser()))
            self.novel_author = ", ".join(authors)
        except Exception as e:
            logger.warning("Failed to parse novel authors | %s", e)

        for item in self.parse_chapter_list_in_browser():
            if isinstance(item, Chapter):
                self.chapters.append(item)
            elif isinstance(item, Volume):
                self.volumes.append(item)

    def parse_title_in_browser(self) -> str:
        """Parse and return the novel title in the browser"""
        return self.parse_title(self.browser.soup)

    def parse_cover_in_browser(self) -> str:
        """Parse and return the novel cover image in the browser"""
        return self.parse_cover(self.browser.soup)

    def parse_authors_in_browser(self) -> Generator[Tag, None, None]:
        """Parse and return the novel author in the browser"""
        yield from self.parse_authors(self.browser.soup)

    def parse_chapter_list_in_browser(
        self,
    ) -> Generator[Union[Chapter, Volume], None, None]:
        """Parse and return the volumes and chapters in the browser"""
        return self.parse_chapter_list(self.browser.soup)

    def download_chapter_body_in_scraper(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter.url)
        body = self.select_chapter_body(soup)
        return self.parse_chapter_body(body)

    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        self.visit_chapter_page_in_browser(chapter)
        body = self.select_chapter_body_in_browser()
        return self.parse_chapter_body(body)

    def visit_chapter_page_in_browser(self, chapter: Chapter) -> None:
        """Open the Chapter URL in the browser"""
        self.visit(chapter.url)

    def select_chapter_body_in_browser(self) -> Tag:
        """Select the tag containing the chapter text in the browser"""
        return self.select_chapter_body(self.browser.soup)
