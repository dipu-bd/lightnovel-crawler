# -*- coding: utf-8 -*-

import logging
import re
from typing import List
from urllib.parse import quote_plus

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException
from lncrawl.models import Chapter, SearchResult

logger = logging.getLogger(__name__)


class NovelFullMeCrawler(Crawler):
    base_url = "https://novelfull.me/"

    def search_novel(self, query) -> List[SearchResult]:
        soup = self.get_soup(f"{self.home_url}search?q={quote_plus(query.lower())}")

        return [
            SearchResult(title=a.text.strip(), url=self.absolute_url(a["href"]))
            for a in soup.select(".meta .title a")
            if isinstance(a, Tag)
        ]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        slug = re.search(rf"{self.home_url}(.*?)(/|\?|#|$)", self.novel_url).group(1)

        title_tag = soup.select_one(".book-info .name h1")
        if not isinstance(title_tag, Tag):
            raise LNException("No title found")

        self.novel_title = title_tag.get_text().strip()

        logger.info("Novel title: %s", self.novel_title)

        img_tag = soup.select_one(".img-cover img")
        if isinstance(img_tag, Tag):
            self.novel_cover = self.absolute_url(img_tag["data-src"])

        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = ", ".join(
            [a.text.strip() for a in soup.select(".detail a[href*='/authors/'] span")]
        )
        logger.info("Novel author: %s", self.novel_author)

        soup = self.get_soup(f"{self.home_url}api/novels/{slug}/chapters?source=detail")

        for a in reversed(soup.select("#chapter-list > li > a")):
            self.chapters.append(
                Chapter(
                    id=len(self.chapters) + 1,
                    title=a.select_one(".chapter-title").text.strip(),
                    url=self.absolute_url(a["href"]),
                )
            )

    def download_chapter_body(self, chapter: Chapter):
        soup = self.get_soup(chapter.url)
        contents = soup.select_one("#chapter__content .content-inner")
        self.cleaner.clean_contents(contents)

        return str(contents)
