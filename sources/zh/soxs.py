# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler


logger = logging.getLogger(__name__)


class Soxc(Crawler):
    base_url = ["https://www.soxs.cc/"]

    def read_novel_info(self):
        self.novel_url = self.novel_url.replace("/book/", "/")
        self.novel_url = self.novel_url.replace(".html", "/")
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".xiaoshuo h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.get_text()
        logger.info(f"Novel title: {self.novel_title}")

        self.novel_author = soup.select_one(".xiaoshuo h6").get_text()
        logger.info(f"Novel Author: {self.novel_author}")

        possible_novel_cover = soup.select_one(".book_cover img")
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["src"])
        logger.info(f"Novel Cover: {self.novel_cover}")

        logger.info("Getting chapters...")
        for chapter in soup.select(".novel_list dd a"):
            url = self.absolute_url(chapter["href"])
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = len(self.chapters) // 100 + 1
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "url": url,
                    "volume": vol_id,
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        title = soup.select_one(".read_title h1").text.strip()
        chapter["title"] = title

        content = soup.select(".content")
        content = "\n".join(str(p) for p in content)
        content = content.replace(self.novel_url, "")
        content = content.replace("soxscc", "mtlrealm.com ")
        return content
