# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

OWN_CHAPTER = re.compile(r"^\s*chapter\s+\d+", re.I)


class RubyMaybeTranslationsCrawler(SoupTemplate):
    base_url = ["https://rubymaybetranslations.com/"]

    novel_title_selector = "h1"
    chapter_body_selector = ".entry-content"

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        novel.tags = [
            t for t in (a.text.strip() for a in soup.select("a[rel~='tag'], a[href*='/tag/']")) if t
        ]

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        here = self.absolute_url(novel.url).split("?")[0].rstrip("/")
        origin = self.scraper.origin.rstrip("/")
        rows = {}
        for anchor in tag.select(".entry-content a[href]"):
            href = self.absolute_url(str(anchor.get("href") or "")).split("?")[0].rstrip("/")
            if not href.startswith(origin) or href == here:
                continue
            if not OWN_CHAPTER.match(anchor.get_text(" ", strip=True)):
                continue
            rows.setdefault(href, anchor)
        return list(rows.values())
