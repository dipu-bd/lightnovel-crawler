# -*- coding: utf-8 -*-

import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = "%ssearch?q=%s"


class MangaBuddyCrawler(Crawler):
    has_manga = True
    base_url = "https://mangabuddy.com/"

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % (self.home_url, query))

        results = []
        for book in soup.select(".book-detailed-item .meta"):
            a = book.select_one(".title a")

            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        slug = re.search(rf"{self.home_url}(.*?)(/|\?|$)", self.novel_url).group(1)

        self.novel_title = soup.select_one(".book-info .name h1").text.strip()

        logger.info("Novel title: %s", self.novel_title)

        img_src = soup.select_one(".img-cover img")

        if img_src:
            self.novel_cover = self.absolute_url(img_src["src"])

        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = ", ".join(
            [a.text.strip() for a in soup.select(".detail a[href*='/authors/'] span")]
        )
        logger.info("Novel author: %s", self.novel_author)

        soup = self.get_soup(
            f"{self.home_url}api/manga/{slug}" + "/chapters?source=detail"
        )

        for a in reversed(soup.select("#chapter-list > li > a")):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.select_one(".chapter-title").text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        server = soup.find("script", string=re.compile(r"var mainServer = "))
        images = soup.find("script", string=re.compile(r"var chapImages = "))

        main_server = re.search(r'var mainServer = "(.*)";', server.text).group(1)
        img_list = (
            re.search(r"var chapImages = \'(.*)\'", images.text).group(1).split(",")
        )

        image_urls = [f'<img src="{main_server}{img}">' for img in img_list]

        return "<p>" + "</p><p>".join(image_urls) + "</p>"
