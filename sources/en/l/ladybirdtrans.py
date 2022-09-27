# -*- coding: utf-8 -*-

import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class lazybirdtranslations(Crawler):
    base_url = "https://lazybirdtranslations.wordpress.com/"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                ".entry-meta",
                ".inline-ad-slot",
                ".has-text-align-center",
                "#jp-post-flair",
                ".entry-footer",
            ]
        )

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_novel_cover = soup.select_one('meta[property="og:image"]')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["content"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        authors = []
        for a in soup.select("figcaption"):
            authors.append(a.text.strip())
        self.novel_author = ", ".join(authors)
        logger.info("Novel author: %s", self.novel_author)

        # Stops external links being selected as chapters
        chapters = soup.select(
            '.wp-block-table tr td a[href*="lazybirdtranslations.wordpress.com/2"]'
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

        # Adds proper chapter ttile, only problem is some are in 2 parts so there named the same.
        if "Chapter" in soup.select_one("h2").text:
            chapter["title"] = soup.select_one("h2").text
        else:
            chapter["title"] = chapter["title"]

        body_parts = soup.select_one("div.entry-content")
        assert isinstance(body_parts, Tag), "No chapter body"

        for content in body_parts.select("p"):
            for bad in ["[Index]", "[Previous]", "[Next]"]:
                if bad in content.text:
                    content.extract()

        return self.cleaner.extract_contents(body_parts)
