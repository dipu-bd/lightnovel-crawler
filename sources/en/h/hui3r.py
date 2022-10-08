# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class hui3rCrawler(Crawler):
    base_url = "https://hui3r.wordpress.com/"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                'span[style*="color:#ffffff;"]',
                "footer.entry-meta",
                ".sharedaddy",
            ]
        )

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".single-entry-content h3 a")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        # TODO: Having trouble grabbing cover without error message (cannot identify image file <_io.BytesIO object at 0x000002CC03335F40>).
        # self.novel_cover = self.absolute_url(
        #     soup.select_one('.single-entry-content p img')
        # logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "Translated by hui3r"
        logger.info("Novel author: %s", self.novel_author)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one(".single-entry-content")
        for notoc in toc_parts.select(
            ".sharedaddy, .inline-ad-slot, .code-block, script, .adsbygoogle"
        ):
            notoc.extract()

        # Extract volume-wise chapter entries
        chapters = soup.select(
            '.single-entry-content ul li a[href*="hui3r.wordpress.com/2"]'
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
        body_parts = soup.select_one(".single-entry-content")
        assert isinstance(body_parts, Tag), "No chapter body"
        return self.cleaner.extract_contents(body_parts)
