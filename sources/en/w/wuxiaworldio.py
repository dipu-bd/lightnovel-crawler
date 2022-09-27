# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://wuxiaworld.io/search.ajax?type=&query=%s"


class WuxiaWorldIo(Crawler):
    base_url = [
        "https://wuxiaworld.io/",
        "https://wuxiaworld.name/",
    ]

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            [
                r"^translat(ed by|or)",
                r"(volume|chapter) .?\d+",
            ]
        )

    def search_novel(self, query):
        """Gets a list of {title, url} matching the given query"""
        soup = self.get_soup(search_url % query)

        results = []
        for novel in soup.select("li"):
            a = novel.select_one(".resultname a")
            info = novel.select_one("a:nth-of-type(2)")
            info = info.text.strip() if info else ""
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "Latest: %s" % info,
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        # self.novel_title = soup.select_one('h1.entry-title').text.strip()
        possible_title = soup.select_one("div.entry-header h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("span.info_image img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = soup.select("div.truyen_info_right li")[1].text.strip()
        logger.info("Novel author: %s", self.novel_author)

        for a in reversed(soup.select("#list_chapter .chapter-list a")):
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
        contents = soup.select_one("div.content-area")
        return self.cleaner.extract_contents(contents)
