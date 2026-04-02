# -*- coding: utf-8 -*-
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, Volume
from lncrawl.templates.wordpress import WordpressTemplate


class DaoNovelCrawler(WordpressTemplate):
    base_url = "https://daonovel.com/"
    madara_body_from_paragraphs = True
    madara_search_max_results = 20

    def parse_search_item_info(self, soup: PageSoup) -> str:
        info = []
        latest = soup.select_one(".latest-chap .chapter a")
        if latest:
            info.append(latest.text.strip())
        votes = soup.select_one(".rating .total_votes")
        if votes:
            info.append("Rating: " + votes.text.strip())
        return " | ".join(info)

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        chapter_list_url = self.absolute_url("ajax/chapters", novel.url)
        ch_soup = self.scraper.post_soup(chapter_list_url, headers={"accept": "*/*"})
        return reversed(list(ch_soup.select("li.wp-manga-chapter a")))
