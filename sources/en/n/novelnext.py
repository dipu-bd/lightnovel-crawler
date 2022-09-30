# -*- coding: utf-8 -*-
import logging
from typing import List
from urllib.parse import quote_plus

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException
from lncrawl.models import Chapter, SearchResult

logger = logging.getLogger(__name__)


class NovelNextCrawler(Crawler):
    base_url = "https://novelnext.com/"

    def search_novel(self, query) -> List[SearchResult]:
        soup = self.get_soup(
            f"{self.home_url}ajax/search-novel?keyword={quote_plus(query.lower())}"
        )

        return [
            SearchResult(
                title=a.text.strip(),
                url=self.absolute_url(a["href"]),
            )
            for a in soup.select("a[href^='http']")
            if isinstance(a, Tag)
        ]

    def read_novel_info(self):
        self.novel_url = self.novel_url.split("#")[0]

        soup = self.get_soup(self.novel_url)

        title_tag = soup.select_one("h3.title")
        if not isinstance(title_tag, Tag):
            raise LNException("No title found")

        self.novel_title = title_tag.text.strip()

        image_tag = soup.select_one(".books .book img")

        self.novel_cover = self.absolute_url(image_tag["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        split_url = self.novel_url.split("/")
        self.novel_id = split_url[len(split_url) - 1]
        logger.info("Novel id: %s", self.novel_id)

        chapters_soup = self.get_soup(
            f"{self.home_url}ajax/chapter-archive?novelId={self.novel_id}"
        )

        for a in chapters_soup.select(".list-chapter li a"):
            self.chapters.append(
                Chapter(
                    id=len(self.chapters) + 1,
                    title=a.text.strip(),
                    url=self.absolute_url(a["href"]),
                )
            )

    def download_chapter_body(self, chapter: Chapter):
        soup = self.get_soup(chapter.url)
        contents = soup.select_one("#chr-content")
        self.cleaner.clean_contents(contents)

        return str(contents)
