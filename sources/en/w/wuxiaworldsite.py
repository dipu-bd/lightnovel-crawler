# -*- coding: utf-8 -*-
import logging

from bs4.element import Tag
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
full_chapter_list_url = "https://wuxiaworldsite.co/get-full-list.ajax?id=%s"


class WuxiaSiteCo(Crawler):
    base_url = "https://wuxiaworldsite.co/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".read-item h1")
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".read-item .img-read img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select_one(".read-item .content-reading p:first-child")
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info("Novel author: %s", self.novel_author)

        possible_id = soup.select_one(".story-introduction__toggler .show-more-list")
        assert isinstance(possible_id, Tag)
        self.novel_id = possible_id["data-id"]
        logger.info("Novel Id: %s", self.novel_id)

        soup = self.get_soup(full_chapter_list_url % self.novel_id)

        for a in soup.select("a"):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": "Chapter %d" % chap_id,
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.content-story")
        assert isinstance(contents, Tag)

        for bad in contents.select('p[style="display: none"], script, ins'):
            bad.extract()

        return "\n".join([str(p) for p in contents.select("p") if p.text.strip()])
