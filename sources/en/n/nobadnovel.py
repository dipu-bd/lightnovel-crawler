# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_NUMBER = re.compile(r"/chapter-(\d+)")


class NoBadNovelCrawler(SoupTemplate):
    base_url = ["https://www.nobadnovel.com/"]

    novel_title_selector = "h1"
    # The theme is Tailwind, so there is no semantic class to hold on to; the prose is the
    # only block that sets a reading measure, which `leading-8` marks.
    chapter_body_selector = "div[class*='leading-8']"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # The whole list is on the novel page, but so are a cover link and a "Start
        # Reading" button pointing at chapter one. Keyed by number, those collapse into
        # the real row instead of duplicating it.
        rows = {}
        for anchor in tag.select("a[href]"):
            match = CHAPTER_NUMBER.search(str(anchor.get("href") or ""))
            if match and (anchor.text or "").strip():
                number = int(match.group(1))
                if number not in rows or len((anchor.text or "").strip()) > len(
                    (rows[number].text or "").strip()
                ):
                    rows[number] = anchor
        return [rows[number] for number in sorted(rows)]
