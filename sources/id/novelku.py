# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class NovelkuCrawler(Crawler):
    base_url = "https://novelku.id/"

    def initialize(self):
        self.home_url = "https://novelku.id/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.get_text(" ")
        logger.info("Novel title: %s", self.novel_title)

        possible_author = soup.select_one(".author-content a")
        assert possible_author, "No novel author"
        self.novel_author = possible_author.get_text(" ")
        logger.info("Novel author: %s", self.novel_author)

        meta = soup.select("head meta")
        possible_image = None
        for m in meta:
            if m.get("property") == "og:image":
                possible_image = m.get("content")
                break

        if possible_image is None:
            cover = soup.select_one(".summary_image a img")
            if cover:
                self.novel_cover = self.absolute_url(cover["data-src"])
        else:
            self.novel_cover = self.absolute_url(possible_image)

        logger.info("Novel cover: %s", self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select("li.wp-manga-chapter a")

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
                    "title": a.get_text(" - ", strip=True) or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        logger.info("download body chapter: %s", chapter["url"])
        soup = self.get_soup(chapter["url"])
        contents = soup.select("div.text-left p")
        body = [str(p) for p in contents if p.text.strip()]
        return "<p>" + "</p><p>".join(body) + "</p>"
