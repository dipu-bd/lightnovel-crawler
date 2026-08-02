# -*- coding: utf-8 -*-
import logging
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_HOST = "maplesan9.wordpress.com"


class MaplesanTlCrawler(SoupTemplate):
    base_url = [
        "https://maplesantl.com/",
        "https://maplesan9.wordpress.com/",
    ]

    chapter_body_selector = ".entry-content"

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        # The index page carries no heading element at all — the novel's name is only in
        # the OpenGraph tag, and the default reads a tag's text rather than its content.
        tag = soup.select_one('meta[property="og:title"]')
        novel.title = str(tag.get("content") or "").strip() if tag else ""

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        novel.tags = [
            t for t in (a.text.strip() for a in soup.select("a[rel~='tag'], a[href*='/tag/']")) if t
        ]

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        here = self.absolute_url(novel.url).split("?")[0].rstrip("/")
        rows = {}
        for anchor in tag.select(".entry-content a[href]"):
            href = self.absolute_url(str(anchor.get("href") or "")).split("?")[0].rstrip("/")
            if href == here or not anchor.text.strip():
                continue
            # The index lives on maplesantl.com while every chapter it points at is
            # published on the WordPress host, so same-origin filtering would empty the
            # list rather than trim it.
            if CHAPTER_HOST not in href:
                continue
            rows.setdefault(href, anchor)
        return list(rows.values())
