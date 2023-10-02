# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
ajax_url = "https://jaomix.ru/wp-admin/admin-ajax.php"


class JaomixCrawler(Crawler):
    base_url = [
        "https://jaomix.ru/",
    ]

    def initialize(self):
        self.init_executor(
            workers=1
        )

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".desc-book h1")
        if possible_title:
            self.novel_title = possible_title.get_text()

        logger.info("Novel title: %s", self.novel_title)

        for p in soup.select("#info-book p"):
            text = p.text.strip()
            if "Автор" in text:
                self.novel_author = text.split(":")[1].strip()
                break

        logger.info("Novel author: %s", self.novel_author)

        possible_synopsis = soup.select_one("div#desc-tab")
        if possible_synopsis:
            self.novel_synopsis = self.cleaner.extract_contents(possible_synopsis)

        logger.info("Novel synopsis: %s", self.novel_synopsis)

        img_src = soup.select_one("div.img-book img")

        if img_src:
            self.novel_cover = self.absolute_url(img_src["src"])

        for a in reversed(soup.select('.flex-dow-txt a')):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a['href']),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".entry-content .entry")
        return self.cleaner.extract_contents(contents)
