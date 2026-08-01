# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, List

from lncrawl.core import Novel, PageSoup, SoupTemplate

logger = logging.getLogger(__name__)

CHAPTER_API = "https://chap.heliosarchive.online/wp-json/wp/v2/posts"
PAGE_SIZE = 500
TAG_MODULUS = 1999999997


class MVLEmpyrCrawler(SoupTemplate):
    base_url = [
        "https://www.mvlempyr.io/",
        "https://www.mvlempyr.com/",
    ]

    novel_title_selector = ".novel-title"
    novel_cover_selector = "img.novel-image2"
    novel_synopsis_selector = ".synopsis"
    novel_tags_selector = "a.g-t-link"
    chapter_body_selector = "#chapter-content"

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        code = soup.select_one("#novel-code").text.strip()
        if not code:
            return
        # Chapters live in a separate WordPress install and are grouped by a tag whose id
        # the site derives from the novel code rather than storing. The exponentiation is
        # theirs; reproducing it is the only way to ask for one novel's chapters.
        tag = pow(7, int(code), TAG_MODULUS)

        posts: List[Dict[str, Any]] = []
        page = 1
        while True:
            batch = self.scraper.get_json(
                f"{CHAPTER_API}?tags={tag}&per_page={PAGE_SIZE}&page={page}"
            )
            if not isinstance(batch, list) or not batch:
                break
            posts += batch
            if len(batch) < PAGE_SIZE:
                break
            page += 1

        posts.sort(key=lambda post: int((post.get("acf") or {}).get("chapter_number") or 0))
        for post in posts:
            acf = post.get("acf") or {}
            number = acf.get("chapter_number")
            novel.add_chapter(
                title=acf.get("ch_name") or f"Chapter {number}",
                url=self.absolute_url(f"/chapter/{code}-{number}"),
            )
