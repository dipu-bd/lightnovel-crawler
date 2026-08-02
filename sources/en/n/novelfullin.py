# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core import Chapter, PageSoup, SoupTemplate

logger = logging.getLogger(__name__)

SPACES = re.compile(r"\s+")


class NovelFullInCrawler(SoupTemplate):
    base_url = ["https://www.novelfull.in/"]

    novel_title_selector = "h1"

    # `.chapter-content` names the list on a novel page and the prose on a chapter page.
    # The whole list is there in reading order, with no pager. The novel page also carries a
    # `.latest-chapters` panel that runs newest first — not this, or the book arrives backwards.
    chapter_list_selector = "div.chapter-content ul li a"

    chapter_body_selector = ".chapter-content"

    def parse_chapter_title(self, soup: PageSoup, chapter: Chapter) -> None:
        # The markup breaks each title across several indented lines.
        chapter.title = SPACES.sub(" ", soup.get_text(" ", strip=True)).strip()
