# -*- coding: utf-8 -*-

import logging
from urllib.parse import quote

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class AllNovelCrawler(Crawler):
    base_url = [
        "https://allnovel.org/",
        "https://www.allnovel.org/",
    ]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])

    def search_novel(self, query):
        soup = self.get_soup(self.home_url + "search?keyword=" + quote(query))

        results = []
        for div in soup.select(".list-truyen > .row"):
            a = div.select_one(".truyen-title a")
            if not isinstance(a, Tag):
                continue
            info = div.select_one(".text-info .chapter-text")
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": info.text.strip() if info else "",
                }
            )
        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        image = soup.select_one(".info-holder .book img")
        assert isinstance(image, Tag), "No title found"

        self.novel_title = image["alt"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        authors = soup.select('.info-holder .info a[href*="/author/"]')
        self.novel_author = ", ".join([a.text.strip() for a in authors])
        logger.info("Novel author: %s", self.novel_author)

        possible_id = soup.select_one("input#truyen-id")
        assert possible_id, "No novel id"

        self.novel_id = possible_id["value"]

        soup = self.get_soup(
            self.home_url + "ajax-chapter-option?novelId=%s" % self.novel_id
        )

        for opt in soup.select("select option"):
            chap_id = len(self.chapters) + 1
            self.chapters.append(
                {
                    "id": chap_id,
                    "title": opt.text,
                    "url": self.absolute_url(opt["value"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div#chapter-content")
        assert isinstance(contents, Tag), "No chapter content"
        self.cleaner.clean_contents(contents)
        return str(contents)
