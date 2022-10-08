# -*- coding: utf-8 -*-

import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class CrescentMoonCrawler(Crawler):
    base_url = "https://crescentmoon.blog/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"class": "entry-title"}).text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one("div.entry-content p a")["href"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = soup.select("div.entry-content p")[2].text.strip()
        logger.info("Novel author: %s", self.novel_author)

        toc = None
        a = soup.select("div.entry-content p")
        for idx, item in enumerate(a):
            if "table of contents" in item.text.strip().lower():
                toc = a[idx + 1]
        assert toc, "No table of contents"

        for x in toc.find_all("a"):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(x["href"]),
                    "title": x.text.strip() or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select("div.entry-content")
        return self.cleaner.extract_contents(contents)
