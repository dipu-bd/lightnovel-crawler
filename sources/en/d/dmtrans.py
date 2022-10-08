# -*- coding: utf-8 -*-

import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class DMTranslations(Crawler):
    base_url = [
        "https://dmtranslationscn.com/",
    ]

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".entry-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("div.entry-content p img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = "Translated by DM Translations"
        logger.info("Novel author: %s", self.novel_author)

        # Extract volume-wise chapter entries
        chapters = soup.find("div", {"class": "entry-content"}).findAll("a")

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

        body_parts = soup.select_one("div.entry-content")

        for content in body_parts.select("p"):
            for bad in ["Translator- DM", "Previous Chapter", "Next Chapter"]:
                if bad in content.text:
                    content.extract()

        return self.cleaner.extract_contents(body_parts)
