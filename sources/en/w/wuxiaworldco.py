# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote

from lncrawl.core import Chapter, Novel, PageSoup, SearchResult, SoupTemplate

logger = logging.getLogger(__name__)


class WuxiaCoCrawler(SoupTemplate):
    can_search = True
    base_url = [
        "https://www.wuxiaworld.co/",
        "https://m.wuxiaworld.co/",
    ]

    novel_title_selector = "div.book-name"
    novel_author_selector = "div.author span.name"
    novel_cover_selector = "div.book-img img"
    chapter_list_selector = "ul.chapter-list a.chapter-item"
    chapter_title_selector = "div.chapter-name"
    chapter_body_selector = "div.chapter-entity"

    def initialize(self) -> None:
        self.scraper.origin = "https://m.wuxiaworld.co/"
        self.taskman.init_executor(1)
        self.cleaner.bad_text_regex.update(
            [
                r"^translat(ed by|or)",
                r"(volume|chapter) .?\d+",
            ]
        )

    def search(self, query: str):
        soup = self.scraper.get_soup(f"{self.scraper.origin}search/{quote(query)}/1")
        for li in soup.select("ul.result-list li.list-item"):
            name_a = li.select_one("a.book-name")
            if not name_a:
                continue
            href = name_a.get("href")
            author_el = name_a.select_one("font")
            author = author_el.text if author_el else ""
            title = name_a.text.replace(author, "")
            yield SearchResult(
                title=title,
                url=self.absolute_url(href),
                info=f"Author: {author}",
            )

    def build_novel_url(self, novel: Novel) -> str:
        return novel.url.replace("https://www", "https://m")

    def select_chapter_body(self, chapter: Chapter) -> PageSoup:
        soup = self.scraper.get_soup(chapter.url)
        title_text = soup.select_one("h1.chapter-title").text
        if title_text:
            chapter.title = title_text
        return soup.select_one(self.chapter_body_selector)
