# -*- coding: utf-8 -*-

import logging
from typing import List
from urllib.parse import quote_plus

from lncrawl.core import Chapter, LegacyCrawler, SearchResult

logger = logging.getLogger(__name__)

search_url = "https://www.wuxia.city/search?q=%s"


class WuxiaCityCrawler(LegacyCrawler):
    base_url = [
        "https://wuxia.city",
    ]

    # This source offers no manga/manhua/manhwa.
    has_manga = False

    # Set True if this source contains machine translations.
    has_mtl = True

    def search_novel(self, query: str) -> List[SearchResult]:
        query = quote_plus(str(query).lower())
        soup = self.get_soup(search_url % query)
        entries = [
            (
                e.select_one("div.book-caption a[href] h4"),
                e.select_one("p.book-genres a"),
                e.select_one("span.star[style]").get("style").split(" ")[1].strip(),
            )
            for e in soup.find_all("li", class_="section-item")
        ]
        return [
            SearchResult(
                title=e[0].text,
                url=self.absolute_url(e[0].parent["href"]),
                info=f"{e[1].text} | Score: {e[2].strip()}",
            )
            for e in entries
        ]

    def read_novel_info(self) -> None:
        soup = self.get_soup(f"{self.novel_url}/table-of-contents")

        self.novel_title = soup.select_one("h1.book-name").text
        self.novel_author = soup.select_one("dl.author dd").text
        self.novel_cover = self.absolute_url(soup.select_one("div.book-img img[src]").get("src"))

        vol_id = 0
        soup = self.get_soup(f"{self.novel_url}/table-of-contents")
        for a in reversed(soup.select(".book-chapters a[href]")):
            p = a.select_one(".chapter-name")
            p.decompose(".chapter-num")
            self.chapters.append(
                Chapter(
                    id=len(self.chapters) + 1,
                    volume=vol_id,
                    title=p.text,
                    url=self.absolute_url(a["href"]),
                )
            )

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter.url)
        content = soup.select_one("#chapter-content, .chapter-content")
        return self.cleaner.extract_contents(content)
