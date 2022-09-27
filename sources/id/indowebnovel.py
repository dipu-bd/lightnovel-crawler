# -*- coding: utf-8 -*-
import logging


from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class IndowebnovelCrawler(Crawler):
    base_url = "https://indowebnovel.id/"

    def initialize(self):
        self.home_url = "https://indowebnovel.id/"

    def read_novel_info(self):
        # url = self.novel_url.replace('https://yukinovel.me', 'https://yukinovel.id')
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = "Translated by Indowebnovel"
        logger.info("Novel author: %s", self.novel_author)

        possible_image = soup.select_one("div.lightnovel-thumb img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select("div.lightnovel-episode ul li a")

        chapters.reverse()

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
        contents = soup.select("#main article p")
        body = [str(p) for p in contents if p.text.strip()]
        return "<p>" + "</p><p>".join(body) + "</p>"
