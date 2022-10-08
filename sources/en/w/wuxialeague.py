# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class WuxiaLeagueCrawler(Crawler):
    base_url = "https://www.wuxialeague.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("#bookinfo .d_title h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("#bookimg img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_authors = [
            a.text for a in soup.select('#bookinfo a[href*="/author/"]')
        ]
        self.novel_author = ", ".join(possible_authors)
        logger.info("Novel author: %s", self.novel_author)

        for a in soup.select("#chapterList li a"):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
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
        for p in soup.select("#TextContent > p"):
            if not p.text.strip():
                continue
            clean_first = "".join(re.findall(r"([a-z0-9]+)", p.text.lower()))
            clean_title = "".join(re.findall(r"([a-z0-9]+)", chapter["title"].lower()))
            if clean_first == clean_title:
                continue
            body += str(p).strip()
        return body
