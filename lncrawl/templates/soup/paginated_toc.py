from abc import abstractmethod
from typing import Generator, Iterable

from bs4 import BeautifulSoup, Tag

from ...models import Chapter
from .general import GeneralSoupTemplate


class PaginatedSoupTemplate(GeneralSoupTemplate):
    is_template = True

    def parse_chapter_list(self, soup: BeautifulSoup) -> None:
        for page in self.generate_page_soups(soup):
            tags = self.select_chapter_tags(page)
            for tag in tags:
                next_id = len(self.chapters) + 1
                item = self.parse_chapter_item(tag, next_id)
                self.chapters.append(item)

    @abstractmethod
    def generate_page_soups(
        self, soup: BeautifulSoup
    ) -> Generator[BeautifulSoup, None, None]:
        """Generate soups for each chapter list pages"""
        raise NotImplementedError()

    @abstractmethod
    def select_chapter_tags(self, soup: BeautifulSoup) -> Iterable[Tag]:
        """Select chapter list item tags from a chapter list page soup"""
        raise NotImplementedError()

    @abstractmethod
    def parse_chapter_item(self, a: Tag, id: int) -> Chapter:
        """Parse a single chapter from chapter list item tag"""
        raise NotImplementedError()
