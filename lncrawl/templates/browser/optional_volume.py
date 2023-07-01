from typing import Generator, Union

from bs4 import Tag

from ...models import Chapter, Volume
from ..soup.optional_volume import OptionalVolumeSoupTemplate
from .general import GeneralBrowserTemplate


class OptionalVolumeBrowserTemplate(GeneralBrowserTemplate, OptionalVolumeSoupTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def parse_chapter_list_in_browser(
        self,
    ) -> Generator[Union[Chapter, Volume], None, None]:
        vol_id = 0
        chap_id = 0
        for vol in self.select_volume_tags_in_browser():
            if not isinstance(vol, Tag):
                continue
            vol_id += 1
            vol_item = self.parse_volume_item_in_browser(vol, vol_id)
            yield vol_item
            for tag in self.select_chapter_tags_in_browser(vol):
                if not isinstance(tag, Tag):
                    continue
                chap_id += 1
                item = self.parse_chapter_item_in_browser(tag, chap_id, vol_item)
                item.volume = vol_id
                yield item

        if chap_id > 0:
            return

        vol_id = 0
        chap_id = 0
        parent = self.browser.soup.select_one("html")
        for tag in self.select_chapter_tags_in_browser(parent):
            if not isinstance(tag, Tag):
                continue
            if chap_id % 100 == 0:
                vol_id = chap_id // 100 + 1
                vol_item = self.parse_volume_item_in_browser(parent, vol_id)
                yield vol_item
            chap_id += 1
            item = self.parse_chapter_item_in_browser(tag, chap_id, vol_item)
            item.volume = vol_id
            yield item

    def select_volume_tags_in_browser(self) -> Generator[Tag, None, None]:
        """Select volume list item tags from the browser"""
        return self.select_volume_tags(self.browser.soup)

    def parse_volume_item_in_browser(self, tag: Tag, id: int) -> Volume:
        """Parse a single volume from volume list item tag from the browser"""
        return self.parse_volume_item(tag, id)

    def select_chapter_tags_in_browser(self, tag: Tag) -> Generator[Tag, None, None]:
        """Select chapter list item tags from volume tag from the browser"""
        return self.select_chapter_tags(tag)

    def parse_chapter_item_in_browser(self, tag: Tag, id: int, vol: Volume) -> Chapter:
        """Parse a single chapter from chapter list item tag from the browser"""
        return self.parse_chapter_item(tag, id, vol)
