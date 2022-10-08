# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = "https://www.machine-translation.org/novel/search/?keywords=%s"


class MachineTransOrg(Crawler):
    has_mtl = True
    base_url = "https://www.machine-translation.org/"

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update([r"^Refresh time: \d+-\d+-\d+$"])

    def search_novel(self, query):
        url = search_url % quote(query.lower())
        logger.debug("Visiting: %s", url)
        soup = self.get_soup(url)

        results = []
        for li in soup.select(".book-list-info > ul > li"):
            results.append(
                {
                    "title": li.select_one("a h4 b").text.strip(),
                    "url": self.absolute_url(li.select_one(".book-img a")["href"]),
                    "info": li.select_one(".update-info").text.strip(),
                }
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("div.title h3 b")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = soup.select_one("div.title h3 span").text
        logger.info("Novel author: %s", self.novel_author)

        possible_image = soup.select_one(".book-img img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        for a in reversed(soup.select("div.slide-item a")):
            ch_title = a.text.strip()
            ch_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": ch_id,
                    "volume": vol_id,
                    "title": ch_title,
                    "url": self.absolute_url(a["href"]),
                }
            )

        logger.debug(
            "%d chapters and %d volumes found", len(self.chapters), len(self.volumes)
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        body = soup.select_one(".read-main .read-context")
        return self.cleaner.extract_contents(body)
