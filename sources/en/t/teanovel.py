# -*- coding: utf-8 -*-
import json
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException

logger = logging.getLogger(__name__)


class TeaNovelCrawler(Crawler):
    base_url = "https://www.teanovel.com"

    def initialize(self):
        self.init_executor(
            workers=4
        )

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        script_tag = soup.select_one("script#__NEXT_DATA__")
        if not isinstance(script_tag, Tag):
            raise LNException("No script data found")

        next_data = json.loads(script_tag.get_text())

        novel_data = next_data["props"]["pageProps"]["novel"]

        self.novel_title = novel_data["name"]
        self.novel_author = novel_data["author"]

        img_tag = soup.select_one("main img[src*='_next/']")
        if isinstance(img_tag, Tag):
            self.novel_cover = self.absolute_url(img_tag["src"])

        chapters = self.get_soup(self.novel_url + "/chapter-list").select("a.border-b")
        for chapter in chapters:
            chapter_id = len(self.chapters) + 1
            self.chapters.append(
                {
                    "id": chapter_id,
                    "title": chapter.select_one("p").get_text(strip=True),
                    "url": self.absolute_url(chapter["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        chapter = self.get_soup(chapter["url"])
        return self.cleaner.extract_contents(chapter.select_one("div.prose"))
