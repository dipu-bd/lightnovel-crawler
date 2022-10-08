# -*- coding: utf-8 -*-
import logging
from concurrent import futures
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_list_url = "https://webnovelindonesia.com/wp-json/writerist/v1/chapters?category=%s&perpage=100&order=ASC&paged=%s"


class WebnovelIndonesia(Crawler):
    base_url = "https://webnovelindonesia.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".breadcrumb .breadcrumb-item.active")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.section-novel img[class*="lazy"]')["data-src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = soup.select_one(
            '.section-novel li a[href*="/aut/"]'
        ).text.strip()
        logger.info("Novel author: %s", self.novel_author)

        possible_chapter_pages = soup.select("#js-chpater-jump > div.jump-to")

        if not len(possible_chapter_pages):
            possible_chapter_pages = [{"data-paged": "1"}]

        novel_id = soup.select_one("#sortable-table")["data-category"]

        logger.info("Downloading chapters...")
        futures_to_check = dict()
        for div in possible_chapter_pages:
            page = div["data-paged"]
            url = chapter_list_url % (novel_id, page)
            task = self.executor.submit(self.extract_chapter_list, url)
            futures_to_check[task] = page

        temp_chapters = dict()
        for future in futures.as_completed(futures_to_check):
            page = int(futures_to_check[future])
            temp_chapters[page] = future.result()

        logger.info("Building sorted chapter list...")
        for page in sorted(temp_chapters.keys()):
            self.volumes.append({"id": page})
            for chap in temp_chapters[page]:
                chap["volume"] = page
                chap["id"] = 1 + len(self.chapters)
                self.chapters.append(chap)

    def extract_chapter_list(self, url):
        temp_list = []
        logger.debug("Visiting: %s", url)
        data = self.get_json(url)
        for item in data:
            temp_list.append(
                {
                    "title": item["post_title"],
                    "url": self.absolute_url(item["permalink"]),
                }
            )
        return temp_list

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        body = ""
        for p in soup.select("#content > p"):
            if p.text.strip():
                body += str(p).strip()

        return body
