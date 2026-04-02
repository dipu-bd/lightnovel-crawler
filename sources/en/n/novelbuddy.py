# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional
from urllib.parse import urlencode

from lncrawl.core import BrowserTemplate, Chapter, Novel, PageSoup, Volume

logger = logging.getLogger(__name__)


class NovelbuddyCrawler(BrowserTemplate):
    base_url = ["https://novelbuddy.io/"]

    has_mtl = True

    search_item_list_selector = "div.book-item"
    search_item_title_selector = "div.title h3 a[href]"
    search_item_url_selector = search_item_title_selector

    novel_title_selector = "div.name.box h1"
    novel_cover_selector = "div.img-cover img[data-src]"
    novel_summary_selector = "div.section-body.summary span"
    chapter_body_selector = "div.chapter__content div.content-inner"

    def build_search_url(self, query: str) -> str:
        return f"{self.scraper.origin}search?{urlencode({'q': query})}"

    def parse_author(self, soup: PageSoup, novel: Novel) -> None:
        for p in soup.select("div.meta.box.mt-1.p-10"):
            if p.select_one("strong").text.strip("Author"):
                authors = [a.text for a in p.select("a")]
                novel.author = ", ".join(authors)

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        for p in soup.select("div.meta.box.mt-1.p-10 p"):
            if p.select_one("strong").text.strip("Genre"):
                novel.tags = [a.text.strip() for a in p.select("a")]

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        script = tag.select_one("div.layout script").text
        pattern = r"(var|let|const)\s+(\w+)\s*=\s*(.*?);"
        matches = re.findall(pattern, script)

        variables = {}
        for _, name, value in matches:
            variables[name] = value.strip()

        soup = self.scraper.get_soup(
            f"https://novelbuddy.io/api/manga/{variables['bookId']}/chapters?source=detail"
        )
        return soup.select("ul li")[::-1]

    def parse_chapter_item(self, soup: PageSoup, chapter_id: int) -> Chapter:
        return Chapter(
            id=chapter_id,
            title=soup.select_one("strong").text,
            url=f"{self.scraper.origin}{soup.select_one('a')['href']}",
        )
