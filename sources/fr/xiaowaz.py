# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException

logger = logging.getLogger(__name__)


class XiaowazCrawler(Crawler):
    base_url = ["https://xiaowaz.fr/"]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [".abh_box_business", ".footnote_container_prepare"]
        )

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        title_tag = soup.select_one("h1.card_title")
        if not isinstance(title_tag, Tag):
            raise LNException("No title found")

        self.novel_title = title_tag.text.strip()

        image_tag = soup.select_one(".entry-content img")
        if isinstance(image_tag, Tag):
            self.novel_cover = self.absolute_url(image_tag["src"])

        logger.info("Novel cover: %s", self.novel_cover)

        for a in soup.select(".entry-content a[href*='/articles/']"):
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".entry-content")
        self.cleaner.clean_contents(contents)

        return str(contents)
