from abc import abstractmethod
from typing import Generator, Union

from bs4 import BeautifulSoup, Tag

from ...models import Chapter, Volume
from .general import GeneralSoupTemplate


class ChapterWithVolumeSoupTemplate(GeneralSoupTemplate):
    def parse_chapter_list(
        self, soup: BeautifulSoup
    ) -> Generator[Union[Chapter, Volume], None, None]:
        vol_id = 0
        chap_id = 0
        for vol in self.select_volume_tags(soup):
            if not isinstance(vol, Tag):
                continue
            vol_id += 1
            vol_item = self.parse_volume_item(vol, vol_id)
            yield vol_item
            for tag in self.select_chapter_tags(vol, vol_item):
                if not isinstance(tag, Tag):
                    continue
                chap_id += 1
                item = self.parse_chapter_item(tag, chap_id, vol_item)
                item.volume = vol_id
                yield item

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
        """Select chapter list item tags from volume tag"""
        raise NotImplementedError()

    @abstractmethod
    def parse_chapter_item(self, tag: Tag, id: int, vol: Volume) -> Chapter:
        """Parse a single chapter from chapter list item tag"""
        raise NotImplementedError()
