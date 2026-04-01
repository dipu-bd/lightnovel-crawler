# -*- coding: utf-8 -*-
import logging
from typing import Iterable
from urllib.parse import urlencode

from lncrawl.core import Novel, PageSoup, SoupTemplate

logger = logging.getLogger(__name__)


class AsiaNovelNetCrawler(SoupTemplate):
    base_url = [
        "https://www.asianovel.net/",
        "https://www.wuxiasky.net/",
    ]

    search_item_list_selector = "ul#search-result-list > li"
    search_item_title_selector = "h3.card__title a"
    search_item_url_selector = "h3.card__title a"
    search_item_info_selector = "span.card__footer-chapters"
    search_item_tags_selector = "div.card__tag-list"

    novel_title_selector = "div.story__identity h1.story__identity-title"
    novel_cover_selector = ".story__thumbnail a"
    novel_author_selector = "div.story__identity div.story__identity-meta a.author"
    novel_genres_selector = "div.novel-container div#edit-genre a[href*='/genre/']"
    novel_summary_selector = "section.story__summary"
    novel_chapters_selector = "section.story__chapters li > a"
    novel_chapter_body_selector = "section#chapter-content"

    chapter_list_selector = "section.story__chapters li > a"
    chapter_body_selector = "section#chapter-content"

    def initialize(self) -> None:
        self.taskman.init_executor(ratelimit=1)
        self.cleaner.bad_css.update(["div.asian-ads-top-content", "div.asian-ads-bottom-content"])

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        params = {"s": query, "post_type": "fcn_story"}
        soup = self.scraper.post_soup(f"{self.scraper.origin}?{urlencode(params)}")
        return soup.select(self.search_item_list_selector)

    def parse_search_item_info(self, soup: PageSoup) -> str:
        chapters = soup.select_one(self.search_item_info_selector)
        tags = soup.select_one(self.search_item_tags_selector)
        info = ""
        if chapters:
            info += f"{chapters.text.strip()} chapters | "
        if tags:
            info += f"Tags: {tags.text.strip()}"
        return info

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(self.search_item_tags_selector)
        tag.decompose("div.yarpp-related")
        novel.synopsis = tag.text
