# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

# Chapters are dated posts; the novel page is a hand-written index that links them.
CHAPTER_PATH = re.compile(r"/\d{4}/\d{2}/\d{2}/")


class GooseberryTlCrawler(SoupTemplate):
    base_url = ["https://gooseberrytl.wordpress.com/"]

    novel_title_selector = "h1.entry-title"

    # `#content` and `main` also match but carry the comment thread with them.
    chapter_body_selector = ".entry-content"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        rows = {}
        for anchor in tag.select(".entry-content a[href]"):
            href = self.absolute_url(str(anchor.get("href") or "")).split("?")[0]
            if not href.startswith(self.scraper.origin) or not CHAPTER_PATH.search(href):
                continue
            if anchor.get_text(" ", strip=True):
                rows.setdefault(href.rstrip("/"), anchor)
        return list(rows.values())
