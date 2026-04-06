# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Chapter, LegacyCrawler

logger = logging.getLogger(__name__)


class WhatsAWhizzerCrawler(LegacyCrawler):
    base_url = ["https://whatsawhizzerwebnovels.com/"]

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(".page-header-title").text.strip()
        logger.info("Novel title: %s", self.novel_title)

        cover_tag = soup.select_one('meta[property="og:image"]')

        if cover_tag:
            self.novel_cover = cover_tag["content"]

        logger.info("Novel cover: %s", self.novel_cover)

        for a in soup.select(".entry > p > a"):
            self.chapters.append(
                Chapter(
                    id=len(self.chapters) + 1,
                    url=self.absolute_url(a["href"]),
                    title=a.text.strip(),
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("article > div")

        nav_tags = contents.find_all("a", string="Table of Contents")
        for nav in nav_tags:
            nav.parent.extract()

        self.cleaner.clean_contents(contents)

        return str(contents)
