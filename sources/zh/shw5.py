# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Shw5Crawler(Crawler):
    base_url = [
        "https://www.shw5.cc/",
        "https://www.bq99.cc/",
        "https://www.p2wt.com/",
    ]

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".book h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_novel_cover = soup.select_one('.book img')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_synopsis = soup.select_one('.intro dd')
        if possible_synopsis:
            self.novel_synopsis = possible_synopsis.text
        logger.info("Novel synopsis %s", self.novel_synopsis)

        possible_novel_author = soup.select_one('.book .small span')
        if possible_novel_author:
            self.novel_author = possible_novel_author.text
        logger.info("Novel author: %s", self.novel_author)

        volumes = set([])
        chapters = soup.select_one('.listmain')
        for a in chapters.find_all("a", rel=False):
            ch_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": ch_id,
                    "volume": vol_id,
                    "title": a.text,
                    "url": self.absolute_url(a["href"]),
                }
            )

        self.volumes = [{"id": x, "title": ""} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("#chaptercontent")
        return self.cleaner.extract_contents(contents)
