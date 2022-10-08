import logging
from abc import abstractmethod
from typing import Generator

from bs4 import BeautifulSoup, Tag

from ...core.crawler import Crawler
from ...core.exeptions import LNException
from ...models import Chapter

logger = logging.getLogger(__name__)


class GeneralSoupTemplate(Crawler):
    def read_novel_info(self) -> None:
        soup = self.get_soup(self.novel_url)

        try:
            self.novel_title = self.parse_title(soup)
        except Exception as e:
            raise LNException("Failed to parse novel title", e)

        try:
            self.novel_cover = self.parse_cover(soup)
        except Exception as e:
            logger.warn("Failed to parse novel cover | %s", e)

        try:
            authors = set(list(self.parse_authors(soup)))
            self.novel_author = ", ".join(authors)
        except Exception as e:
            logger.warn("Failed to parse novel authors | %s", e)

        self.parse_chapter_list(soup)

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter.url)

        try:
            body = self.select_chapter_body(soup)
            assert body
            return self.parse_chapter_body(body)
        except Exception as e:
            raise LNException("Failed to parse chapter body", e)

    @abstractmethod
    def parse_title(self, soup: BeautifulSoup) -> str:
        """Parse and return the novel title"""
        raise NotImplementedError()

    @abstractmethod
    def parse_cover(self, soup: BeautifulSoup) -> str:
        """Parse and return the novel cover image"""
        raise NotImplementedError()

    @abstractmethod
    def parse_authors(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        """Parse and return the novel authors"""
        raise NotImplementedError()

    @abstractmethod
    def parse_chapter_list(self, soup: BeautifulSoup) -> None:
        """Parse and set the volumes and chapters"""
        raise NotImplementedError()

    @abstractmethod
    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        """Select the tag containing the chapter text"""
        raise NotImplementedError()

    def parse_chapter_body(self, tag: Tag) -> str:
        """Extract the clean HTML content from the tag containing the chapter text"""
        return self.cleaner.extract_contents(tag)
