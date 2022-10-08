# -*- coding: utf-8 -*-

import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class ExiledRebelsScanlations(Crawler):
    base_url = "https://exiledrebelsscanlations.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"class": "entry-title"}).text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".post-thumbnail img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = "Translated by ExR"
        logger.info("Novel author: %s", self.novel_author)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.lcp_catlist p [href*="exiledrebelsscanlations.com/"]'
        )

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
        contents = soup.select("div#wtr-content")
        return self.cleaner.extract_contents(contents)
