# -*- coding: utf-8 -*-
import logging
from typing import Iterable
from urllib.parse import quote_plus

from lncrawl.core import Chapter, Novel, PageSoup, SearchResult, SoupTemplate

logger = logging.getLogger(__name__)


class LightNovelPubOrg(SoupTemplate):
    base_url = [
        "https://lightnovelpub.org/",
        "https://www.lightnovelpub.org/",
    ]

    can_search = True

    novel_title_selector = "div.novel-info h1"
    novel_cover_selector = "div.novel-cover-container img[src]"
    novel_author_selector = "p.novel-author a.author-link"
    novel_tags_selector = "div.genre-tags span"
    novel_synopsis_selector = "div.summary-content"

    chapter_body_selector = "div.chapter-content"

    def search(self, query: str) -> Iterable[SearchResult]:
        url = f"api/search/?q={quote_plus(query.lower())}&search_type=title"
        for novel in self.scraper.get_json(self.absolute_url(url))["novels"]:
            yield SearchResult(
                title=novel["title"],
                url=self.absolute_url("novel/" + novel["slug"]),
                info=f"Latest chapter: {novel['latest_chapter_number']}",
            )

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        # The novel page links only the first chapter; the rest are reachable by number, and
        # the count is the first figure in the stats grid.
        stat = soup.select_one("div.novel-stats-grid span.stat-value")
        total = int(stat.get_text(strip=True).replace(",", ""))
        base = self.absolute_url(novel.url).split("?")[0].rstrip("/")
        for number in range(1, total + 1):
            novel.add_chapter(title=f"Chapter {number}", url=f"{base}/chapter/{number}/")

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.scraper.get_soup(self.build_chapter_url(chapter))
        # The list carries no titles, so the real one is only knowable here.
        title = soup.select_one(".chapter-title")
        if title:
            chapter.title = title.get_text(strip=True)
        self.parse_chapter_body(soup.select_one(self.chapter_body_selector), chapter)
