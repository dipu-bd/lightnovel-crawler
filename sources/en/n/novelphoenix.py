# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

# Each row ends with how long ago the chapter went up.
POSTED_AGO = re.compile(r"\s*\d+\s+(?:second|minute|hour|day|week|month|year)s?\s+ago\s*$", re.I)
SPACES = re.compile(r"\s+")


class NovelPhoenixCrawler(SoupTemplate):
    base_url = ["https://novelphoenix.com/"]

    novel_title_selector = "h1"

    # `article` and `main` also hold the text, but each wraps it in the post header.
    chapter_body_selector = "#content"

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        # The novel page links only the newest chapter; the list lives one level down.
        url = self.absolute_url(novel.url).split("?")[0].rstrip("/") + "/chapters"
        soup = self.scraper.get_soup(url)
        return soup.select("ul.chapter-list li a[href]")

    def parse_chapter_title(self, soup: PageSoup, chapter: Chapter) -> None:
        # A row runs number, title and timestamp together with no separators between the
        # spans, so the text has to be read with one inserted.
        text = SPACES.sub(" ", soup.get_text(" ", strip=True))
        chapter.title = POSTED_AGO.sub("", text).strip()
