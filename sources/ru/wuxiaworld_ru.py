# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core import Novel, PageSoup
from lncrawl.templates.wpcategory import WpCategoryTemplate

logger = logging.getLogger(__name__)

BOILERPLATE = re.compile(r"\s*Ранобэ\s+Новелла\s*$", re.I)


class WuxiaWorldRuCrawler(WpCategoryTemplate):
    base_url = ["https://wuxiaworld.ru/"]
    language = "ru"

    can_search = True

    chapter_body_selector = ".entry-content"

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(".entry-content img[src], article img[src]")
        if tag:
            novel.cover_url = self.absolute_url(str(tag.get("src")))

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        # The only tag on a novel is its own name, which says nothing a reader does not
        # already have.
        title = (novel.title or "").strip().lower()
        novel.tags = [
            t
            for t in (a.text.strip() for a in soup.select("a[rel~='tag']"))
            if t and t.lower() != title
        ]

    def chapter_title(self, title: str, prefix: str) -> str:
        return BOILERPLATE.sub("", super().chapter_title(title, prefix)).strip()
