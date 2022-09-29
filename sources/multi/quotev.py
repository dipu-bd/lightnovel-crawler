# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException

logger = logging.getLogger(__name__)


class QuotevCrawler(Crawler):
    base_url = ["https://www.quotev.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_css.update([".nosel"])

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        title_tag = soup.select_one("#quizHeaderTitle h1")
        if not isinstance(title_tag, Tag):
            raise LNException("No title found")

        self.novel_title = title_tag.text.strip()

        image_tag = soup.select_one("meta[property='og:image']")
        if isinstance(image_tag, Tag):
            self.novel_cover = self.absolute_url(image_tag["content"])

        logger.info("Novel cover: %s", self.novel_cover)

        for a in soup.select("#rselectList a"):
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("#rescontent")
        self.cleaner.clean_contents(contents)

        return str(contents)
