# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

BOOK_ID = re.compile(r"/story/[^/]*?_(\d+)")
CHAPTER_HREF = re.compile(r"/story/[^/]+/[^/]+_(\d+)/?$")
MAX_PAGES = 400


class MegaNovelCrawler(SoupTemplate):
    base_url = ["https://www.meganovel.com/"]

    novel_title_selector = "h1"
    chapter_body_selector = ".read-content"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        match = BOOK_ID.search(self.absolute_url(novel.url))
        if not match:
            return []
        book_id = match.group(1)

        # The catalogue pages overlap: each shows twenty links, ten of them repeats of the
        # page before. Reading until a page contributes nothing new is what finds the end,
        # since no page count is published anywhere.
        rows = {}
        for page in range(1, MAX_PAGES + 1):
            soup = self.scraper.get_soup(f"https://www.meganovel.com/book_catalog/{book_id}/{page}")
            before = len(rows)
            for anchor in soup.select("a[href]"):
                href = str(anchor.get("href") or "")
                found = CHAPTER_HREF.search(href)
                if found and book_id in href:
                    rows.setdefault(int(found.group(1)), anchor)
            if len(rows) == before:
                break
        return [rows[key] for key in sorted(rows)]
