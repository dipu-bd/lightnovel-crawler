# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_PATH = re.compile(r"/series/[^/]+/\d+/chapter-(\d+)")


class RevengerNovelCrawler(SoupTemplate):
    base_url = ["https://revengernovel.com/"]

    novel_title_selector = "h1"
    # Each row prints the chapter name and how long ago it was posted; without this the
    # anchor's own text runs them together as "Chapter 111 months ago".
    chapter_title_selector = ".chapter-info h3"
    chapter_body_selector = ".chapter-content"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # A chapter URL carries an opaque id as well as its number
        # (`/series/<slug>/100/chapter-47`); only the number orders the list. The page also
        # has "Read Now" and "Latest" shortcuts pointing at the same chapters under a
        # *different* id, and those ids 404 — so rows are identified by the title cell only
        # a real row has, not by the URL shape.
        rows = {}
        for anchor in tag.select("a[href]"):
            match = CHAPTER_PATH.search(str(anchor.get("href") or ""))
            if match and anchor.select_one(self.chapter_title_selector):
                rows[int(match.group(1))] = anchor
        return [rows[number] for number in sorted(rows)]
