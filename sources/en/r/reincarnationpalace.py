# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class ReincarnationPalace(Crawler):
    base_url = "https://reincarnationpalace.com/"

    def initialize(self) -> None:
        self.cleaner.bad_css.update([".sharedaddy"])
        self.cleaner.bad_tags.update(["a"])

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("div.elementor-image img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = soup.select("div.elementor-widget-container p")[
            6
        ].text.strip()
        logger.info("Novel author: %s", self.novel_author)

        # Extract volume-wise chapter entries
        # TODO: I've found one chapters it can't download,
        # it has a ` or %60 at end of url which seems to make crawler ignore it
        # for some reason. If anyone know how to fix please do so.
        chapters = soup.select('h4 a[href*="reincarnationpalace"]')

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
