# -*- coding: utf-8 -*-
import logging

from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class DivineDaoLibrary(Crawler):
    base_url = "https://www.divinedaolibrary.com/"

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("article header .entry-title")
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("article .entry-content img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        for h3 in soup.select("article .entry-content h3"):
            text = h3.text.strip()
            if text.startswith("Author"):
                self.novel_author = text[len("Author:") :].strip()
                break
        logger.info("Novel author: %s", self.novel_author)

        soup.select(".entry-content ul li span a")

        for a in soup.select(".entry-content ul li span a"):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        body = ""
        for span in soup.select(
            'article .entry-content > p span[style="font-weight:400"]'
        ):
            if not span.text.strip():
                continue
            body += "<p>" + span.text.strip() + "</p>\n"

        return body
