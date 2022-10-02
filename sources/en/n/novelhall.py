# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class NovelhallCrawler(Crawler):
    has_mtl = True
    base_url = "https://www.novelhall.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".book-info h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("div.book-img img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        author = soup.select("div.book-info div.total.booktag span.blue")[0]
        author.select_one("p").extract()
        self.novel_author = author.text.strip()
        logger.info("Novel author: %s", self.novel_author)

        for a in soup.select("div#morelist.book-catalog ul li a"):
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

        contents = soup.select_one("div#htmlContent.entry-content")
        for ads in contents.select("div"):
            ads.extract()

        return str(contents)
