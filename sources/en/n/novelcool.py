# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class NovelCool(Crawler):
    has_manga = True
    base_url = "https://www.novelcool.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.bookinfo-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = soup.select_one(
            "span", {"itemprop": "creator"}
        ).text.strip()
        logger.info("Novel author: %s", self.novel_author)

        possible_image = soup.select_one("div.bookinfo-pic img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])

        chapters = soup.select(".chapter-item-list a")
        chapters.reverse()

        for x in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(x["href"]),
                    "title": x.text.strip() or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        chapter_title = soup.select_one(".chapter-title")
        chapter_start = soup.select_one(".chapter-start-mark")
        body_parts = chapter_start.parent

        # FIXED: Chapters title removed.
        if chapter_title:
            chapter_title.extract()

        chapter_start.extract()

        for report in body_parts.find("div", {"model_target_name": "report"}):
            report.extract()

        # Removes End of Chapter junk text.
        for junk in body_parts.find("p", {"class": "chapter-end-mark"}):
            junk.extract()

        return self.cleaner.extract_contents(body_parts)
