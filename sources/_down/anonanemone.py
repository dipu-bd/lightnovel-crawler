# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Anonanemone(Crawler):
    base_url = [
        "https://anonanemone.wordpress.com/",
        "https://www.anonanemone.wordpress.com/",
    ]

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".entry-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one(".wp-block-image img")["data-orig-file"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.entry-content p [href*="anonanemone.wordpress.com/2"]'
        )

        for a in chapters:
            chap_id = 1 + len(self.chapters)
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

    def initialize(self) -> None:
        self.cleaner.bad_css.update(["div#jp-post-flair"])
        self.cleaner.bad_text_regex.update(
            [
                r"[Index]",
                r"[Previous]",
                r"[Next]",
            ]
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        body_parts = soup.select_one(".entry-content")
        return self.cleaner.extract_contents(body_parts)
