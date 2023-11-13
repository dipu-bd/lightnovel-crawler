# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://whitemoonlightnovels.com/?s=%s"


class NovelsEmperorCrawler(Crawler):
    base_url = ["https://whitemoonlightnovels.com/"]

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select("div > article"):
            a = tab.select_one("div > article div.mdthumb a")
            title = a["href"][39:].replace("-", " ")
            img = tab.select_one("img")["src"]
            results.append(
                {
                    "title": title,
                    "url": self.absolute_url(a["href"]),
                    "img": img,
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        author = soup.select(".serval a")
        if len(author) == 2:
            self.novel_author = author[0].text + " (" + author[1].text + ")"
        else:
            self.novel_author = author[0].text
        logger.info("Novel author: %s", self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one("img.size-post-thumbnail")["src"]
        ).split("?")[0]
        logger.info("Novel cover: %s", self.novel_cover)

        for a in soup.select("div.eplister ul li a"):
            ch_title = a.select_one("div.epl-title").text
            ch_id = [int(x) for x in re.findall(r"\d+", ch_title)]
            ch_id = ch_id[0] if len(ch_id) else len(self.chapters) + 1
            self.chapters.append(
                {
                    "id": ch_id,
                    "title": ch_title,
                    "url": self.absolute_url(a["href"]),
                }
            )

        logger.debug(
            "%d chapters and %d volumes found", len(self.chapters), len(self.volumes)
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.epcontent")
        contents = self.cleaner.extract_contents(contents)
        return str(contents)
