# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_NUMBER = re.compile(r"-ch(\d+)(?:[-_].*)?/?$", re.I)


class KinkyTranslationsCrawler(SoupTemplate):
    base_url = ["https://kinkytranslations.com/"]

    novel_title_selector = ".entry-title"
    chapter_body_selector = ".entry-content"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # Chapters are ordinary posts under a date path, so the novel slug is what ties
        # them to this novel and the trailing `-chN` is what orders them.
        slug = self.absolute_url(novel.url).rstrip("/").rsplit("/", 1)[-1]
        rows = {}
        for anchor in tag.select("a[href]"):
            href = str(anchor.get("href") or "")
            match = CHAPTER_NUMBER.search(href)
            if match and slug in href:
                rows[int(match.group(1))] = anchor
        return [rows[number] for number in sorted(rows)]
