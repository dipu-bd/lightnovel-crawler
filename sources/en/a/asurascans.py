# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_NUMBER = re.compile(r"/chapter/(\d+)/?$")


class AsuraScansCrawler(SoupTemplate):
    base_url = ["https://asurascans.com/"]

    novel_title_selector = "h1"
    chapter_title_selector = "div[class*='min-w-0']"
    chapter_body_selector = "div[class*='max-w-[65ch]']"

    def initialize(self) -> None:
        self.cleaner.bad_css.update({"h1", "hr"})

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # Free and paid chapters are laid out differently, and the list also carries
        # "First Chapter" and "Latest Chapter" shortcuts pointing back into itself. The
        # title cell is what both real rows share and neither shortcut has.
        rows = {}
        for anchor in tag.select("a[href]"):
            match = CHAPTER_NUMBER.search(str(anchor.get("href") or ""))
            if match and anchor.select_one(self.chapter_title_selector):
                rows[int(match.group(1))] = anchor
        return [rows[number] for number in sorted(rows)]
