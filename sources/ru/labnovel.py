# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class LabnovelCrawler(Crawler):
    base_url = ["https://labnovel.ru/"]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".main-block-book__title h1")
        if possible_title:
            self.novel_title = possible_title.get_text()

        logger.info("Novel title: %s", self.novel_title)

        possible_synopsis = soup.select_one("div[class*='_desc']")
        if possible_synopsis:
            self.novel_synopsis = possible_synopsis.get_text()

        img_src = soup.select_one(".main-block-book__img img")
        if img_src:
            self.novel_cover = self.absolute_url(img_src["src"])

        for chapter in reversed(soup.select("div.chapter-list a")):
            chap_id = 1 + (len(self.chapters))

            self.chapters.append(
                {
                    "id": chap_id,
                    "title": chapter["title"],
                    "url": self.absolute_url(chapter["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.select_one("div.editblock")
        return self.cleaner.extract_contents(content)
