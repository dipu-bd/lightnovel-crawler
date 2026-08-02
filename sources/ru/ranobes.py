# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

TOC_PATH = re.compile(r"/chapters/[^/]+/?$")
CHAPTER_PATH = re.compile(r"/chapters/[^/]+/(\d+)-")
PAGE_NUMBER = re.compile(r"/page/(\d+)/")


class RanobesCrawler(SoupTemplate):
    base_url = ["https://ranobes.com/"]

    novel_title_selector = "h1"
    novel_synopsis_selector = "#fs-info"
    chapter_body_selector = "#arrticle"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        toc_url = ""
        for anchor in tag.select("a[href]"):
            href = str(anchor.get("href") or "")
            if TOC_PATH.search(href):
                toc_url = self.absolute_url(href)
                break
        if not toc_url:
            return []

        first = self.scraper.get_soup(toc_url)
        last_page = max(
            (
                int(m.group(1))
                for m in (
                    PAGE_NUMBER.search(str(a.get("href") or "")) for a in first.select("a[href]")
                )
                if m
            ),
            default=1,
        )

        rows = {}

        def collect(soup: PageSoup) -> None:
            for anchor in soup.select("a[href]"):
                href = str(anchor.get("href") or "").split("#")[0]
                match = CHAPTER_PATH.search(href)
                if match:
                    rows[int(match.group(1))] = anchor

        collect(first)
        for number in range(2, last_page + 1):
            collect(self.scraper.get_soup(f"{toc_url.rstrip('/')}/page/{number}/"))

        return [rows[key] for key in sorted(rows)]
