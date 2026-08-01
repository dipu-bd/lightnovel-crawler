# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

VOLUME_CHAPTER = re.compile(r"volume-(\d+)-chapter-(\d+)", re.I)
CHAPTER_ONLY = re.compile(r"chapter-(\d+)", re.I)


class StabbingWithASyringeCrawler(SoupTemplate):
    base_url = ["https://stabbingwithasyringe.home.blog/"]

    novel_title_selector = ".entry-title"
    chapter_body_selector = ".entry-content"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # The index is prose with the chapters linked inline, so the page chrome links have
        # to be excluded by scope rather than by pattern; inside the post body, a link that
        # extends the novel's own URL is a chapter.
        stem = self.absolute_url(novel.url).split("?")[0].rstrip("/")
        rows = {}
        for anchor in tag.select(".entry-content a[href]"):
            href = str(anchor.get("href") or "").split("?")[0]
            if not href.startswith(stem) or href.rstrip("/") == stem:
                continue
            match = VOLUME_CHAPTER.search(href)
            if match:
                key = (int(match.group(1)), int(match.group(2)))
            else:
                simple = CHAPTER_ONLY.search(href)
                if not simple:
                    continue
                key = (0, int(simple.group(1)))
            rows[key] = anchor
        return [rows[key] for key in sorted(rows)]
