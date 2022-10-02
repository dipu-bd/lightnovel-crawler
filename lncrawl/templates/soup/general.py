from abc import abstractmethod

from bs4 import BeautifulSoup, Tag

from ...core.crawler import Crawler
from ...models import Chapter


class GeneralSoupTemplate(Crawler):
    is_template = True

    def read_novel_info(self) -> None:
        soup = self.get_soup(self.novel_url)
        self.parse_title(soup)
        self.parse_cover(soup)
        self.parse_authors(soup)
        self.parse_chapter_list(soup)

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter.url)
        body = self.select_chapter_body(soup)
        return self.cleaner.extract_contents(body)

    @abstractmethod
    def parse_title(self, soup: BeautifulSoup) -> None:
        """Parse and set the novel title"""
        raise NotImplementedError()

    @abstractmethod
    def parse_cover(self, soup: BeautifulSoup) -> None:
        """Parse and set the novel cover image"""
        raise NotImplementedError()

    @abstractmethod
    def parse_authors(self, soup: BeautifulSoup) -> None:
        """Parse and set the novel author"""
        raise NotImplementedError()

    @abstractmethod
    def parse_chapter_list(self, soup: BeautifulSoup) -> None:
        """Parse and set the volumes and chapters"""
        raise NotImplementedError()

    @abstractmethod
    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        """Select the tag containing the chapter text"""
        raise NotImplementedError()
