# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class AsianHobbyistCrawler(Crawler):
    base_url = "https://www.asianhobbyist.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".main-wrap .background img[data-lazy-src]")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["data-lazy-src"])
        logger.info("Novel cover: %s", self.novel_cover)

        for a in soup.select(".divTable .tableBody div.fn a"):
            title = a.text.strip()
            chap_id = len(self.chapters) + 1
            self.chapters.append(
                {
                    "id": chap_id,
                    "title": title,
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.select_one(".entry-content")
        self.cleaner.extract_contents(content)
        return content.decode_contents()
