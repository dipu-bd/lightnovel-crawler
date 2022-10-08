from abc import abstractmethod
from typing import Generator

from bs4 import BeautifulSoup, Tag

from ...models import Chapter, Volume
from .general import GeneralSoupTemplate


class ChapterWithVolumeSoupTemplate(GeneralSoupTemplate):
    def parse_chapter_list(self, soup: BeautifulSoup) -> None:
        for vol in self.select_volume_tags(soup):
            if not isinstance(vol, Tag):
                continue
            self.process_volumes(vol)

    def process_volumes(self, vol: Tag) -> None:
        vol_id = len(self.volumes) + 1
        vol_item = self.parse_volume_item(vol, vol_id)
        self.volumes.append(vol_item)
        for tag in self.select_chapter_tags(vol, vol_item):
            next_id = len(self.chapters) + 1
            item = self.parse_chapter_item(tag, next_id, vol_item)
            item.volume = vol_id
            self.chapters.append(item)

    @abstractmethod
    def select_volume_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        """Select volume list item tags from the page soup"""
        raise NotImplementedError()

    @abstractmethod
    def parse_volume_item(self, tag: Tag, id: int) -> Volume:
        """Parse a single volume from volume list item tag"""
        raise NotImplementedError()

    @abstractmethod
    def select_chapter_tags(self, tag: Tag, vol: Volume) -> Generator[Tag, None, None]:
        """Select chapter list item tags from volume tag and page soup"""
        raise NotImplementedError()

    @abstractmethod
    def parse_chapter_item(self, tag: Tag, id: int, vol: Volume) -> Chapter:
        """Parse a single chapter from chapter list item tag"""
        raise NotImplementedError()
