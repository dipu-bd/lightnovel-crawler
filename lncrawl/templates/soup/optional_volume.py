from abc import abstractmethod
from typing import Generator, Union

from bs4 import BeautifulSoup, Tag

from ...models import Chapter, Volume
from .general import GeneralSoupTemplate


class OptionalVolumeSoupTemplate(GeneralSoupTemplate):
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
            for tag in self.select_chapter_tags(vol):
                if not isinstance(tag, Tag):
                    continue
                chap_id += 1
                item = self.parse_chapter_item(tag, chap_id, vol_item)
                item.volume = vol_id
                yield item

        if chap_id > 0:
            return

        vol_id = 0
        chap_id = 0
        parent = soup.select_one("html")
        for tag in self.select_chapter_tags(parent):
            if not isinstance(tag, Tag):
                continue
            if chap_id % 100 == 0:
                vol_id = chap_id // 100 + 1
                vol_item = self.parse_volume_item(parent, vol_id)
                yield vol_item
            chap_id += 1
            item = self.parse_chapter_item(tag, chap_id, vol_item)
            item.volume = vol_id
            yield item

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
