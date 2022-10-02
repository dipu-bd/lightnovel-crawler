# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class ReadMangaNato(Crawler):
    base_url = ["https://readmanganato.com/"]

    has_manga = True

    has_mtl = False

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".story-info-right h1")
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(soup.select_one(".info-image img")["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select(
                    'div.story-info-right td.table-value a[href*="author"]'
                )
            ]
        )
        logger.info("%s", self.novel_author)

        for a in reversed(soup.select(".row-content-chapter li.a-h a.chapter-name")):
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

        if "Chapter" in soup.select_one("h1").text:
            chapter["title"] = soup.select_one("h1").text

        contents = soup.select_one("div.container-chapter-reader")
        return self.cleaner.extract_contents(contents)
