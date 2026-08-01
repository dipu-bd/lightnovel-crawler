# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

BOOK_ID = re.compile(r"(?:shu_(\d+)\.html|/(\d+)(?:_\d+)?/?$)")
CHAPTER_PATH = re.compile(r"/\d+/(\d+)\.html")
AUTHOR_LABEL = re.compile(r"^作\s*者[:：]\s*", re.U)


class ShuhaigeCrawler(SoupTemplate):
    base_url = [
        "https://www.shuhaige.net/",
        "https://m.shuhaige.net/",
    ]

    novel_title_selector = "#info h1, h1"
    novel_cover_selector = "#fmimg img"
    novel_synopsis_selector = "#intro"
    chapter_body_selector = "#content"

    def initialize(self) -> None:
        self.cleaner.bad_css.update({"div.bottem", "div.bottem1", "div.bottem2"})

    def build_novel_url(self, novel: Novel) -> str:
        # The mobile site paginates its chapter list a page at a time; the desktop page
        # for the same book carries every chapter at once, so both forms are normalised
        # to the desktop one and the id is the only thing carried across.
        url = self.absolute_url(novel.url)
        match = BOOK_ID.search(url)
        if not match:
            return url
        book_id = match.group(1) or match.group(2)
        return f"https://www.shuhaige.net/{book_id}/"

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        meta = soup.select_one('meta[property="og:novel:author"]')
        if meta and meta.get("content"):
            novel.author = str(meta.get("content")).strip()
            return
        for line in soup.select("#info p"):
            text = (line.text or "").replace("\xa0", "").strip()
            if AUTHOR_LABEL.match(text):
                novel.author = AUTHOR_LABEL.sub("", text)
                return

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # The newest handful are repeated above the full list, so the same chapter appears
        # twice; keying by its numeric id collapses those and orders the rest.
        rows = {}
        for anchor in tag.select("a[href]"):
            match = CHAPTER_PATH.search(str(anchor.get("href") or ""))
            if match:
                rows[int(match.group(1))] = anchor
        return [rows[key] for key in sorted(rows)]
