# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

# Chapters are ordinary posts under a date permalink; the index page links them by hand.
CHAPTER_PATH = re.compile(r"/\d{4}/\d{2}/\d{2}/")


class SilverNekoScanlationsCrawler(SoupTemplate):
    base_url = ["https://silvernekoscanlations.home.blog/"]

    novel_title_selector = "h1.entry-title"

    # `#content` and `main` also match, but they carry the comment thread with them.
    chapter_body_selector = ".entry-content"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # The index sits in the same `.entry-content` as its blurb, so it also holds a link
        # to the raw on jjwxc and the theme's share buttons. Only the dated posts on this
        # blog are chapters.
        rows = {}
        for anchor in tag.select(".entry-content a[href]"):
            href = self.absolute_url(str(anchor.get("href") or "")).split("?")[0]
            if not href.startswith(self.scraper.origin) or not CHAPTER_PATH.search(href):
                continue
            if anchor.get_text(" ", strip=True):
                rows.setdefault(href.rstrip("/"), anchor)
        return list(rows.values())
