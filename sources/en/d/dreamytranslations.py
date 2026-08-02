# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_PATH = re.compile(r"/novel/[^/]+/chapter/(\d+)")
WORD_COUNT = re.compile(r"\s+[\d,]+$")


class DreamyTranslationsCrawler(SoupTemplate):
    base_url = ["https://dreamy-translations.com/"]

    novel_title_selector = "h1"
    chapter_body_selector = "article"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        rows = {}
        for anchor in tag.select("a[href*='/chapter/']"):
            found = CHAPTER_PATH.search(str(anchor.get("href") or ""))
            if not found:
                continue
            number = int(found.group(1))
            current = rows.get(number)
            if current is None or len(anchor.text) > len(current.text):
                rows[number] = anchor
        return [rows[key] for key in sorted(rows)]

    def parse_chapter_title(self, soup: PageSoup, chapter: Chapter) -> None:
        chapter.title = WORD_COUNT.sub("", soup.get_text(" ", strip=True))

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        novel.tags = [
            t for t in (tag.text.strip() for tag in soup.select("a[href*='/genre']")) if t
        ]
