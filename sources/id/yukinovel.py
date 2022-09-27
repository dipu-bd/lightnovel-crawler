# -*- coding: utf-8 -*-
import logging

from bs4 import Comment

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class YukiNovelCrawler(Crawler):
    base_url = [
        "https://yukinovel.me/",
        "https://yukinovel.id/",
    ]

    def initialize(self):
        self.home_url = "https://yukinovel.id/"

    def read_novel_info(self):
        self.novel_url = self.novel_url.replace("https://yukinovel.me/", self.home_url)
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = "Translated by Yukinovel"
        logger.info("Novel author: %s", self.novel_author)

        possible_image = soup.select_one("div.lightnovel-thumb img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select("div.lightnovel-episode ul li a")

        chapters.reverse()

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.entry-content.cl")

        for d in contents.findAll("div"):
            d.extract()

        for comment in contents.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        if contents.findAll("p")[0].text.strip().startswith("Bab"):
            chapter["title"] = contents.findAll("p")[0].text.strip()
            contents.findAll("p")[0].extract()
        else:
            chapter["title"] = chapter["title"]

        logger.debug(chapter["title"])

        return str(contents)
