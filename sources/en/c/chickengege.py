# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Chapter, PageSoup, SoupTemplate

logger = logging.getLogger(__name__)


class ChickenGegeCrawler(SoupTemplate):
    base_url = ["https://www.chickengege.org/"]

    novel_title_selector = "h1.entry-title"
    novel_cover_selector = "img.novelist-cover-image"
    chapter_list_selector = "ul#novelList a, ul#extraList a, table#novelList a"
    chapter_body_selector = "article div.entry-content"

    def initialize(self) -> None:
        self.cleaner.bad_css.update([".m-a-box", ".m-a-box-container"])

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        self.cleaner.clean_contents(soup)
        chapter.body = str(soup)
