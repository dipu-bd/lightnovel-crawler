# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_PATH = re.compile(r"/novel/[^/]+/(\d+)$")
ROW_META = re.compile(
    r"\s*(?:منذ\s*)?\d+\s*"
    r"(?:ثانية|ثواني|دقيقة|دقائق|ساعة|ساعات|يوم|أيام|أسبوع|أسابيع|شهر|أشهر|سنة|سنوات)"
    r"\s*[\d,]*\s*$"
)
MAX_TOC_PAGES = 200


class SuNovelsCrawler(SoupTemplate):
    base_url = ["https://sunovels.com/"]

    chapter_body_selector = ".chapter-content"

    def initialize(self) -> None:
        self.cleaner.bad_css.update({"p.d-none", ".d-none"})

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:title"]')
        novel.title = str(tag.get("content") or "").strip() if tag else ""

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        novel.tags = [t for t in (a.text.strip() for a in soup.select("a[href*='/genre']")) if t]

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        base = self.absolute_url(novel.url).split("?")[0].rstrip("/")

        def collect(soup: PageSoup, rows: dict) -> int:
            seen = 0
            for anchor in soup.select("a[href]"):
                found = CHAPTER_PATH.search(str(anchor.get("href") or ""))
                if not found:
                    continue
                state = anchor.select_one("svg.fa-lock-open, svg.fa-lock")
                if state is None:
                    continue
                seen += 1
                if "fa-lock-open" in (state.get("class") or []):
                    rows[int(found.group(1))] = anchor
            return seen

        rows: dict = {}
        for page in range(MAX_TOC_PAGES):
            query = "" if page == 0 else f"&page={page}"
            if not collect(self.scraper.get_soup(f"{base}?activeTab=chapters{query}"), rows):
                break
        else:
            logger.warning("Stopped reading the chapter list at page %s", MAX_TOC_PAGES)
        return [rows[key] for key in sorted(rows)]

    def parse_chapter_title(self, soup: PageSoup, chapter: Chapter) -> None:
        chapter.title = ROW_META.sub("", soup.get_text(" ", strip=True)).strip()
