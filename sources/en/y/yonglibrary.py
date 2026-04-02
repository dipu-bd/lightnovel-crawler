# -*- coding: utf-8 -*-
import logging
from typing import List

from lncrawl.core import BrowserTemplate, Novel, PageSoup, SearchResult

logger = logging.getLogger(__name__)


class YongLibraryCrawler(BrowserTemplate):
    base_url = [
        "https://yonglibrary.com/",
    ]

    novel_title_selector = "h1.novel-hero__title"
    novel_cover_selector = ".novel-hero__cover img, img.novel-hero__image"
    novel_genres_selector = ".novel-hero__tags .badge--genre"
    novel_summary_selector = ".insight-content"

    novel_chapter_list_reverse = True
    novel_chapter_list_selector = "li.chapter-item"
    novel_chapter_url_selector = "a.chapter-item__link"
    novel_chapter_title_selector = ".chapter-item__title"
    novel_chapter_body_selector = ".chapter-content__body"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                ".ad-slot",
                ".chapter-companion",
                ".chapter-content__badge",
                "script",
            ]
        )
        self.cleaner.bad_text_regex.update(
            [
                r"window.pubfuturetag = .*})",
            ]
        )

    def search_novel(self, query: str) -> List[SearchResult]:
        url = f"{self.scraper.origin}wp-json/wp/v2/search"
        params = {"search": query, "per_page": 10, "type": "term", "subtype": "category"}
        data = self.scraper.get_json(url, params=params)
        results = []
        for item in data:
            title = item.get("title", "")
            cat_url = item.get("url", "")
            novel_url = cat_url.replace("/category/", "/", 1)
            results.append(SearchResult(title=title, url=novel_url))
        return results

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(".insight-content")
        novel.summary = (tag.find("p") or tag).text
