# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_PATH = re.compile(r"/webnovel/\d+/(\d+)\.html")


class R18NovelCrawler(SoupTemplate):
    base_url = ["https://r18novel.com/"]

    has_mtl = True

    novel_title_selector = "h1"
    chapter_body_selector = "#chr-content"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # Chapters are keyed by an id in the path rather than by a chapter number, and the
        # ids run the other way: the lowest belongs to the newest chapter. Sorting them
        # descending is what puts chapter one first.
        rows = {}
        for anchor in tag.select("a[href]"):
            match = CHAPTER_PATH.search(str(anchor.get("href") or ""))
            if match:
                rows[int(match.group(1))] = anchor
        return [rows[key] for key in sorted(rows, reverse=True)]
