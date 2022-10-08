# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class AncientHeartloss(Crawler):
    base_url = [
        "https://ancientheartloss.com/",
        "https://ancientheartloss.wordpress.com/",
    ]

    def initialize(self) -> None:
        # There is a lot of TN notes at bottom of chapters and junk text I've tried to remove as much as I can.
        self.cleaner.bad_text_regex.update(
            [
                "PREVIOUS CHAPTER",
                "CHAPTER LIST",
                "NEXT CHAPTER",
                "FOLLOW / LIKE / SUBSCRIBE",
                "FOLLOW AND LIKE THIS BLOG",
                "SUBSCRIBE and LIKE",
                "SUBSCRIBE AND LIKE",
                "Please donate any amount to support our group!",
                "Please donate to support our group!",
            ]
        )

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_novel_cover = soup.select_one('meta[property="og:image"]')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["content"])
        logger.info("Novel cover: %s", self.novel_cover)

        # No author names listed
        self.novel_author = "Translated by AncientHeartloss"
        logger.info("Novel author: %s", self.novel_author)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one(".entry-content")
        for notoc in toc_parts.select(".sharedaddy"):
            notoc.extract()

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select('.entry-content p a[href*="ancientheartloss"]')

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
        body_parts = soup.select_one(".entry-content")
        return self.cleaner.extract_contents(body_parts)
