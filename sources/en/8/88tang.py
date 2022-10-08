# -*- coding: utf-8 -*-

import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class TangEatDrinkRead(Crawler):
    base_url = "https://88tangeatdrinkread.wordpress.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        title = soup.select_one("h1.entry-title").text
        self.novel_title = title.rsplit("~", 1)[0].strip()
        logger.debug("Novel title = %s", self.novel_title)

        self.novel_author = "by 88 Tang"
        logger.info("Novel author: %s", self.novel_author)

        # Removes none TOC links.
        toc_parts = soup.select_one(".entry-content")
        for notoc in toc_parts.select(".sharedaddy, .code-block, script, .adsbygoogle"):
            notoc.extract()

        # Extract volume-wise chapter entries
        # TODO: Chapter title are url links, it's the way translator formatted website.
        chapters = soup.select(
            '.entry-content a[href*="88tangeatdrinkread.wordpress.com"]'
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
        contents = soup.select_one("div.entry-content")
        return self.cleaner.extract_contents(contents)
