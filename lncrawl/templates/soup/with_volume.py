from abc import abstractmethod
from typing import Iterable

from bs4 import BeautifulSoup, Tag

from ...models import Chapter, Volume
from .general import GeneralSoupTemplate


class ChapterWithVolumeSoupTemplate(GeneralSoupTemplate):
    def parse_chapter_list(self, soup: BeautifulSoup) -> None:
        for vol in self.select_volume_tags(soup):
            if not isinstance(vol, Tag):
                continue
            vol_id = len(self.volumes) + 1
            vol_item = self.parse_volume_item(vol_id, vol, soup)
            for tag in self.select_chapter_tags(vol_item, vol, soup):
                next_id = len(self.chapters) + 1
                item = self.parse_chapter_item(next_id, tag, vol_item, soup)
                self.chapters.append(item)

    @abstractmethod
    def select_volume_tags(self, soup: BeautifulSoup) -> Iterable[Tag]:
        """Select volume list item tags from the page soup"""
        raise NotImplementedError()

    @abstractmethod
    def parse_volume_item(self, id: int, vol_tag: Tag, soup: BeautifulSoup) -> Volume:
        """Parse a single volume from volume list item tag"""
        raise NotImplementedError()

    @abstractmethod
    def select_chapter_tags(
        self, vol: Volume, vol_tag: Tag, soup: BeautifulSoup
    ) -> Iterable[Tag]:
        """Select chapter list item tags from volume tag and page soup"""
        raise NotImplementedError()

    @abstractmethod
    def parse_chapter_item(
        self, id: int, chap_tag: Tag, vol: Volume, vol_tag: Tag, soup: BeautifulSoup
    ) -> Chapter:
        """Parse a single chapter from chapter list item tag"""
        raise NotImplementedError()
