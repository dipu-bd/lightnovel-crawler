# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class PandaMtlCrawler(Crawler):
    base_url = ["https://pandamtl.com/"]
    has_mtl = True

    def initialize(self):
        self.init_executor(ratelimit=0.99)

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(".entry-title").text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".sertothumb img")
        if isinstance(possible_image, Tag):
            self.novel_cover = possible_image["data-src"]
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select(".sertoauth .serl:nth-child(3) .serval a")
        if possible_author:
            self.novel_author = ", ".join([a.text.strip() for a in possible_author])
        logger.info("Novel author: %s", self.novel_author)

        possible_synopsis = soup.select(".entry-content p")
        if possible_synopsis:
            self.novel_synopsis = "".join([str(p) for p in possible_synopsis])
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        for a in reversed(soup.select(".eplisterfull ul li a")):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.select_one(".epl-title").text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        possible_title = soup.select_one(".epcontent.entry-content h2")
        if isinstance(possible_title, Tag):
            chapter["title"] = possible_title.text.strip()

        contents = soup.select(".epcontent.entry-content p")
        return "".join([str(p) for p in contents])
