# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

MONTHS = "Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık"
# Each anchor ends with when the chapter went up — "Az önce" and "2 saat önce" on the recent
# ones, a plain date such as "6 Haziran 2026" on the rest.
POSTED = re.compile(
    rf"\s+(?:az\s+önce|\d+\s+(?:saniye|dakika|saat|gün|hafta|ay|yıl)\s+önce"
    rf"|\d{{1,2}}\s+(?:{MONTHS})\s+\d{{4}})\s*$",
    re.I,
)
LOCKED = "🔒"
PREMIUM = re.compile(r"giriş gerekli|premium içeriğe", re.I)


class NovelOkurCrawler(SoupTemplate):
    base_url = ["https://novelokur.com.tr/"]
    language = "tr"

    novel_title_selector = "h1"
    chapter_body_selector = ".chapter-content"

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        novel.tags = [t for t in (a.text.strip() for a in soup.select('a[href*="/tur/"]')) if t]

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        # `og:description` is the site's own boilerplate, repeated on every novel.
        novel.synopsis = ""

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        rows = {}
        # The list runs newest first and opens with a "start reading" button pointing at
        # chapter one. Walking it backwards puts the chapters in reading order and lets that
        # button fall out as a duplicate of the entry it shortcuts to.
        for anchor in reversed(tag.select("a[href*='/chapter/']")):
            href = self.absolute_url(str(anchor.get("href") or "")).split("?")[0]
            text = anchor.get_text(" ", strip=True)
            if not text or LOCKED in text:
                continue
            rows.setdefault(href, anchor)
        return list(rows.values())

    def parse_chapter_title(self, soup: PageSoup, chapter: Chapter) -> None:
        chapter.title = POSTED.sub("", soup.get_text(" ", strip=True)).strip()

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        # Most of this site is sold for its own coins: measured, two novels gave away their
        # first 40 of 289 and 50 of 163. A sold chapter answers with a sign-in notice in
        # place of the text, and the lock the list puts on some of them is not reliable —
        # the newest chapter of one of those novels is sold and carries no marker — so the
        # page itself is what decides. An empty body records the chapter as unavailable,
        # which is what it is.
        body = self.cleaner.extract_contents(soup)
        chapter.body = "" if PREMIUM.search(body) else body
