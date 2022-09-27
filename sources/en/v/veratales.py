# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class VeraTales(Crawler):
    base_url = "https://veratales.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1").text.strip()
        logger.info("Novel title: %s", self.novel_title)

        # self.novel_author= soup.find("div",{"class":"novel-author-info"}).find("h4").text.strip()
        self.novel_author = ""
        logger.info("%s", self.novel_author)

        possible_image = soup.select_one("div.card-header a img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        chapters = soup.select("table td a")
        for a in reversed(chapters):
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
        contents = soup.select_one("div.reader-content")
        return self.cleaner.extract_contents(contents)
