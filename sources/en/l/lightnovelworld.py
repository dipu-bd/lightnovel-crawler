# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class LightNovelWorldCrawler(Crawler):
    base_url = "https://lightnovel.world/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_author = soup.select_one("span.textC999").text.strip()
        logger.info("Novel author: %s", self.novel_author)

        possible_title = soup.select_one("li.text1")
        for span in possible_title.select("span"):
            span.extract()
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".book_info_l img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        volumes = set([])
        for a in soup.select("div#chapter_content ul li a"):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

        self.volumes = [{"id": x} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div#content_detail")
        for ads in contents.select("div"):
            ads.extract()

        return str(contents)
