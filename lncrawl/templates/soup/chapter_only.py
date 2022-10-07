from abc import abstractmethod
from typing import Iterable

from bs4 import BeautifulSoup, Tag

from ...models import Chapter
from .general import GeneralSoupTemplate


class ChapterOnlySoupTemplate(GeneralSoupTemplate):
    def parse_chapter_list(self, soup: BeautifulSoup) -> None:
        for tag in self.select_chapter_tags(soup):
            next_id = len(self.chapters) + 1
            item = self.parse_chapter_item(next_id, tag, soup)
            self.chapters.append(item)

    @abstractmethod
    def select_chapter_tags(self, soup: BeautifulSoup) -> Iterable[Tag]:
        """Select chapter list item tags from the page soup"""
        raise NotImplementedError()

    @abstractmethod
    def parse_chapter_item(self, id: int, tag: Tag, soup: BeautifulSoup) -> Chapter:
        """Parse a single chapter from chapter list item tag"""
        raise NotImplementedError()
