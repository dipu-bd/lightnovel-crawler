from abc import abstractmethod
from typing import Generator

from bs4 import BeautifulSoup, Tag

from ...models import Chapter, Volume
from .general import GeneralSoupTemplate


class OptionalVolumeSoupTemplate(GeneralSoupTemplate):
    def parse_chapter_list(self, soup: BeautifulSoup) -> None:
        for vol in self.select_volume_tags(soup):
            if not isinstance(vol, Tag):
                continue
            vol_id = len(self.volumes) + 1
            vol_item = self.parse_volume_item(vol, vol_id)
            self.volumes.append(vol_item)
            for tag in self.select_chapter_tags(vol):
                next_id = len(self.chapters) + 1
                item = self.parse_chapter_item(tag, next_id, vol_item)
                item.volume = vol_id
                self.chapters.append(item)

        if self.chapters:
            return

        parent = soup.select_one("html")
        for tag in self.select_chapter_tags(parent):
            next_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.volumes) != vol_id:
                vol_item = self.parse_volume_item(parent, vol_id)
                self.volumes.append(vol_item)
            vol_item = self.volumes[-1]
            item = self.parse_chapter_item(tag, next_id, vol_item)
            item.volume = vol_item
            self.chapters.append(item)

    def select_volume_tags(self, soup: BeautifulSoup):
        return []

    def parse_volume_item(self, tag: Tag, id: int) -> Volume:
        return Volume(id=id)

    @abstractmethod
    def select_chapter_tags(self, parent: Tag) -> Generator[Tag, None, None]:
        raise NotImplementedError()

    @abstractmethod
    def parse_chapter_item(self, tag: Tag, id: int, vol: Volume) -> Chapter:
        raise NotImplementedError()
