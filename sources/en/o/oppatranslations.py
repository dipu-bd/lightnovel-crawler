# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)


class OppaTranslationsCrawler(SoupTemplate):
    base_url = ["https://www.oppatranslations.com/"]

    novel_title_selector = "header.entry-header h1.entry-title"
    novel_author_selector = "div.entry-content p strong"
    novel_cover_selector = "div.entry-content img"
    chapter_body_selector = "div.entry-content"

    def initialize(self) -> None:
        self.scraper.origin = "https://www.oppatranslations.com/"

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        for author in soup.select("div.entry-content p strong"):
            if author.text.startswith("Author :"):
                novel.author = author.text.replace("Author :", "")
                break

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        needle = novel.url[15:]
        for a in soup.select("div.entry-content p a"):
            href = self.absolute_url(a.get("href"))
            if needle in href:
                novel.add_chapter(url=href, title=a.text)

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        for p in reversed(soup.select("p")):
            if p.find("a") and "TOC" in p.text:
                p.extract()
        center = soup.select_one("div center")
        if center:
            center.extract()
        chapter.body = re.sub(
            "[⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]",
            "",
            str(soup),
            flags=re.UNICODE,
        )
