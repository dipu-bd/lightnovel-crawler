# -*- coding: utf-8 -*-
import logging
from typing import List

from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter, SearchResult

logger = logging.getLogger(__name__)


class LiteroticaCrawler(Crawler):
    base_url = ["https://leafstudio.site/"]

    def initialize(self) -> None:
        self.init_executor(ratelimit=2)

    def search_novel(self, query) -> List[SearchResult]:
        soup = self.get_soup(
            f"{self.home_url}novels?search={query}&type=&language=&status=&sort="
        )
        results = []
        for item in soup.select("a.novel-item"):
            results.append(
                SearchResult(
                    title=item.select_one("p.novel-item-title").text.strip(),
                    url=item["href"],
                )
            )
        return results

    def read_novel_info(self) -> None:
        soup = self.get_soup(self.novel_url)
        self.novel_title = soup.select_one(".title").text
        self.novel_author = "LeafStudio"
        self.novel_synopsis = soup.select_one(".desc_div > p:nth-child(2)").text or None
        self.novel_tags = [item.text for item in soup.select("a.novel_genre")] or None
        self.novel_cover = soup.select_one("#novel_cover")["src"] or None
        for item in soup.select("a.free_chap").__reversed__():
            self.chapters.append(
                dict(id=len(self.chapters) + 1, title=item.text, url=item["href"])
            )

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter["url"])
        chapterText = ""
        for item in soup.select("p.chapter_content"):
            chapterText += self.cleaner.extract_contents(item)
        return chapterText.replace("Login to buy access to this Chapter.", "")
