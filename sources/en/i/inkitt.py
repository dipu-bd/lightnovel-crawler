# -*- coding: utf-8 -*-
import json
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException

logger = logging.getLogger(__name__)


class InkittCrawler(Crawler):
    base_url = ["https://www.inkitt.com/"]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        id_tag = soup.select_one("#reading-lists-block-container")

        if not isinstance(id_tag, Tag):
            raise LNException("Novel id not found")

        self.novel_id = json.loads(id_tag["props"])["storyId"]

        book_data = self.get_json(f"{self.home_url}api/stories/{self.novel_id}")

        self.novel_title = book_data["title"]
        self.novel_cover = book_data["vertical_cover"]["url"]
        self.novel_author = book_data["user"]["name"]

        chapters = book_data["chapters"]

        for chapter in chapters:
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "title": f"{chapter['chapter_number']}. {chapter['name']}",
                    "url": self.absolute_url(
                        f"{self.novel_url.strip('/')}/chapters/{chapter['chapter_number']}"
                    ),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".story-page-text")
        self.cleaner.clean_contents(contents)

        return str(contents)
