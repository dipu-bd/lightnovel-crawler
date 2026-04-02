# -*- coding: utf-8 -*-
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, Volume
from lncrawl.templates.wordpress import WordpressTemplate


class MostNovel(WordpressTemplate):
    base_url = "https://mostnovel.com/"
    chapter_body_selector = ".text-left"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                "div.skiptranslate",
            ]
        )

    def parse_search_item_title(self, soup: PageSoup) -> str:
        tag = soup.select_one(self.search_item_title_selector)
        return tag.text.rsplit(" ", 1)[0].strip()

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        image = soup.select_one(".summary_image a img")
        if image and image.get("alt"):
            novel.title = image["alt"].strip()
        else:
            super().parse_title(soup, novel)

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        image = soup.select_one(".summary_image a img")
        if image:
            src = image.get("data-src") or image.get("src")
            if src:
                novel.cover_url = self.absolute_url(src)
                return
        super().parse_cover(soup, novel)

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        chapter_list_url = self.absolute_url("ajax/chapters", novel.url)
        ch_soup = self.scraper.post_soup(chapter_list_url, headers={"accept": "*/*"})
        tags = []
        for a in reversed(ch_soup.select('.wp-manga-chapter a[href*="/manga"]')):
            for span in a.find_all("span"):
                span.extract()
            tags.append(a)
        return tags
