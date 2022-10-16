# -*- coding: utf-8 -*-

import logging
from bs4 import ResultSet, Tag
from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter

logger = logging.getLogger(__name__)


class NovelUpdatesCom(Crawler):
    base_url = ["https://www.novelupdates.com/", "https://novelupdates.com/"]

    has_manga = False
    has_mtl = False

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                "a[href*='ko-fi.com']",
            ]
        )
        self.cleaner.bad_tag_text_pairs.update(
            {
                "a": [
                    r"ToC",
                    r"<<",
                    r">>"
                ]
            }
        )

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_novel_cover = soup.select_one('meta[property="og:image"]')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["content"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select_one("div#showauthors a")
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info("Novel author: %s", self.novel_author)

        pagination_link = soup.select(".digg_pagination a:not([rel])")
        page_count = (
            int(pagination_link[-1].get_text())
            if isinstance(pagination_link, ResultSet)
            else 1
        )
        logger.info("Chapter list pages: %d" % page_count)

        for page in reversed(range(1, page_count + 1)):
            url = f"{self.novel_url}?pg={page}#myTable"
            soup = self.get_soup(url)
            for a in reversed(soup.select("#myTable a.chp-release")):
                self.chapters.append(
                    Chapter(
                        id=len(self.chapters) + 1,
                        title=a["title"].strip(),
                        url=self.absolute_url(a["href"]),
                    )
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div.entry-content")
        return self.cleaner.extract_contents(contents)
