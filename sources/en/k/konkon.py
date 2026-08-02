# -*- coding: utf-8 -*-
import logging
from typing import Dict, Iterable, Optional

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

CHAPTER_HREF = "/read/chapter/"


class KonkonCrawler(SoupTemplate):
    base_url = ["https://konkon.ink/"]

    novel_title_selector = "h1"
    novel_author_selector = "a[href*='/author/']"

    chapter_body_selector = "article.prose"

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        # The default `keywords` meta holds the title, which has commas in it and so splits
        # into a handful of sentence fragments offered as genres. The real ones are pills,
        # found from the row label rather than their styling, which is all the markup has.
        tags = []
        for label in soup.select("span"):
            if label.get_text(strip=True).lower() not in ("genres", "tags"):
                continue
            for pill in (label.parent or label).select("button"):
                text = pill.get_text(" ", strip=True).lstrip("#").strip()
                if text and text not in tags:
                    tags.append(text)
        novel.tags = tags

    def get_novel_soup(self, novel: Novel) -> PageSoup:
        # Nothing is in the served HTML — the page is a Nuxt shell that fetches its own data,
        # so there is no listing to parse until the app has run.
        return self.scraper.render_soup(
            self.build_novel_url(novel),
            wait_for=f"a[href*='{CHAPTER_HREF}']",
        )

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # Every chapter is linked three times — once from its title, once from a "View"
        # button beside it, and the first again from "Start Reading" at the top. Keeping the
        # longest text per URL keeps the titled one and drops the buttons.
        rows: Dict[str, PageSoup] = {}
        for anchor in tag.select(f"a[href*='{CHAPTER_HREF}']"):
            href = self.absolute_url(str(anchor.get("href") or ""))
            text = anchor.get_text(" ", strip=True)
            if not text:
                continue
            current = rows.get(href)
            if current is None or len(text) > len(current.get_text(" ", strip=True)):
                rows[href] = anchor
        return list(rows.values())

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.scraper.render_soup(
            self.build_chapter_url(chapter),
            wait_for=f"{self.chapter_body_selector} p",
        )
        self.parse_chapter_body(soup.select_one(self.chapter_body_selector), chapter)
