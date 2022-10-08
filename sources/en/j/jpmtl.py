# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

book_url = "https://jpmtl.com/books/%s"
chapters_url = "https://jpmtl.com/v2/chapter/%s/list?state=published&structured=true&direction=false"


class JpmtlCrawler(Crawler):
    has_mtl = True
    base_url = "https://jpmtl.com/"

    def initialize(self):
        self.home_url = "https://jpmtl.com"

    def read_novel_info(self):
        self.novel_id = self.novel_url.split("/")[-1]
        logger.info("Novel Id: %s", self.novel_id)

        self.novel_url = book_url % self.novel_id
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.book-sidebar__title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".book-sidebar__img img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = soup.select_one(
            ".book-sidebar__author .book-sidebar__info"
        ).text.strip()
        logger.info("Novel author: %s", self.novel_author)

        toc_url = chapters_url % self.novel_id

        toc = self.get_json(toc_url)
        for volume in toc:
            self.volumes.append(
                {
                    "id": volume["volume"],
                    "title": volume["volume_title"],
                }
            )
            for chapter in volume["chapters"]:
                chap_id = len(self.chapters) + 1
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": volume["volume"],
                        "url": self.absolute_url(
                            self.novel_url + "/" + str(chapter["id"])
                        ),
                        "title": chapter["title"] or ("Chapter %d" % chap_id),
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select(".chapter-content__content p")

        body = [str(p) for p in contents if p.text.strip()]

        return "<p>" + "</p><p>".join(body) + "</p>"
