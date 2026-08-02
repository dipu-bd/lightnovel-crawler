# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_PATH = re.compile(r"^/[a-z]{2}/book/\d+/\d+$")
PAGE_PATH = re.compile(r"/detail/\d+/page/(\d+)$")


class NovelFulllCrawler(SoupTemplate):
    base_url = ["https://novelfulll.com/"]

    chapter_body_selector = "#chapter-content"

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        novel.tags = [t for t in (a.text.strip() for a in soup.select("a[href*='/genre']")) if t]

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        base = self.absolute_url(novel.url).split("?")[0].rstrip("/")

        def collect(soup: PageSoup, rows: dict) -> None:
            for anchor in soup.select("a[href]"):
                href = str(anchor.get("href") or "")
                if not CHAPTER_PATH.match(href):
                    continue
                current = rows.get(href)
                if current is None or len(anchor.text) > len(current.text):
                    rows[href] = anchor

        rows: dict = {}
        collect(tag, rows)

        last = 1
        for anchor in tag.select("a[href]"):
            found = PAGE_PATH.search(str(anchor.get("href") or ""))
            if found:
                last = max(last, int(found.group(1)))

        for page in range(2, last + 1):
            collect(self.scraper.get_soup(f"{base}/page/{page}"), rows)
        return list(rows.values())
