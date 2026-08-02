# -*- coding: utf-8 -*-
import logging
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)


class OniichanYameteCrawler(SoupTemplate):
    base_url = ["https://oniichanyamete.moe/"]

    novel_title_selector = "h1.entry-title"

    # `#content` also matches but carries the site's page-hierarchy sidebar with it.
    chapter_body_selector = ".entry-content"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # Chapters are WordPress child pages of the novel, and the theme prints the whole
        # page tree in a sidebar — so every novel on the site appears on every page. Only the
        # children of this novel's own path are its chapters.
        base = self.absolute_url(novel.url).split("?")[0].rstrip("/")
        rows = {}
        for anchor in tag.select("a[href]"):
            raw = str(anchor.get("href") or "")
            # A bare fragment or a share link resolves back onto the novel's own path, so
            # "Skip to content" and the theme's share buttons arrive looking like chapters.
            if not raw or raw.startswith("#") or "?" in raw:
                continue
            href = self.absolute_url(raw).split("?")[0].split("#")[0].rstrip("/")
            if not href.startswith(base + "/") or not anchor.get_text(" ", strip=True):
                continue
            rows.setdefault(href, anchor)
        return list(rows.values())
