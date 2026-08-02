# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CANONICAL = "https://novellive.app"
MIRROR_HOST = re.compile(
    r"https?://(?:www\.)?(?:novellive\.(?:app|org)|noveltrust\.com|lightnovelpub\.me)"
)
PAGE_PATH = re.compile(r"/book/[^/]+/(\d+)/?$")


class NovelLiveCrawler(SoupTemplate):
    base_url = [
        "https://novellive.app/",
        "https://novellive.org/",
        "https://noveltrust.com/",
        "https://lightnovelpub.me/",
    ]

    novel_title_selector = ".m-desc h1.tit"
    novel_cover_selector = ".m-imgtxt img"
    novel_author_selector = "a[href*='/author/']"
    novel_tags_selector = ".m-imgtxt a[href*='/genres/']"
    novel_synopsis_selector = ".m-desc .txt"
    chapter_body_selector = ".m-read .txt"

    def canonical_url(self, url: str) -> str:
        return MIRROR_HOST.sub(CANONICAL, url, count=1)

    def build_novel_url(self, novel: Novel) -> str:
        return self.canonical_url(self.absolute_url(novel.url))

    def parse_chapter_url(self, soup: PageSoup, chapter: Chapter) -> None:
        url_tag = soup.select_one(self.chapter_url_selector) or soup
        chapter.url = self.canonical_url(self.absolute_url(url_tag.get("href")))

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        rows = list(tag.select(".m-newest2 .ul-list5 li a"))

        last = 1
        for anchor in tag.select("a[href]"):
            found = PAGE_PATH.search(str(anchor.get("href") or ""))
            if found:
                last = max(last, int(found.group(1)))

        base = self.canonical_url(self.absolute_url(novel.url)).rstrip("/")
        for number in range(2, last + 1):
            soup = self.scraper.get_soup(f"{base}/{number}")
            rows += soup.select(".m-newest2 .ul-list5 li a")
        return rows
