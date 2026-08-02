# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

NOVEL_PATH = re.compile(r"/novel/([^/?#]+)")
PAGE_PATH = re.compile(r"/novel/[^/]+/(\d+)$")
SITE_SUFFIX = re.compile(r"\s*\|\s*JrNovels\.com\s*$", re.I)


class JrNovelsCrawler(SoupTemplate):
    base_url = ["https://jrnovels.com/"]

    chapter_body_selector = "div.p-4.border"

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:title"]')
        title = str(tag.get("content") or "").strip() if tag else ""
        novel.title = SITE_SUFFIX.sub("", title)

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        # `og:image` is the site favicon on every page, which is worse than no cover.
        for tag in soup.select(".card img[src], article img[src], main img[src]"):
            src = str(tag.get("src") or "")
            if src and "favicon" not in src:
                novel.cover_url = self.absolute_url(src)
                return

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        novel.tags = [
            t
            for t in (a.text.strip() for a in soup.select("a[href*='/genre'], a[href*='/tag/']"))
            if t
        ]

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        found = NOVEL_PATH.search(self.absolute_url(novel.url))
        if not found:
            return []
        slug = found.group(1)
        chapter_path = re.compile(rf"/{re.escape(slug)}/(\d+)$")
        origin = self.scraper.origin.rstrip("/")

        def collect(soup: PageSoup, rows: dict) -> None:
            for anchor in soup.select("a[href]"):
                href = self.absolute_url(str(anchor.get("href") or "")).split("?")[0]
                match = chapter_path.search(href)
                if match:
                    rows.setdefault(int(match.group(1)), anchor)

        first = self.scraper.get_soup(f"{origin}/novel/{slug}/1")
        rows: dict = {}
        collect(first, rows)

        # The pager prints the first few numbers and the last one, so the page count comes
        # from the highest it offers rather than from walking a "next" link.
        last = 1
        for anchor in first.select("a[href]"):
            page = PAGE_PATH.search(str(anchor.get("href") or ""))
            if page:
                last = max(last, int(page.group(1)))

        for page in range(2, last + 1):
            collect(self.scraper.get_soup(f"{origin}/novel/{slug}/{page}"), rows)
        return [rows[key] for key in sorted(rows)]
