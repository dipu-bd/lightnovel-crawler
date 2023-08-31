# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://novelsemperor.com/series?title=%s&type=&status="


class NovelsEmperorCrawler(Crawler):
    base_url = ["https://novelsemperor.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            [
                "Thank you for reading this story at novelsemperor.com",
                "immediately rushed \\(Campaign period:",
                "promotion, charge 100 and get 500 VIP coupons!",
            ]
        )

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select("div.xlg\\:grid-cols-8.grid.grid-cols-3 div#card-real"):
            a = tab.select_one("a")
            title = a["href"][33:].replace("-", " ")
            img = tab.select_one("img")["data-src"]
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
        pagination_num = self.get_soup(self.novel_url)
        pagination_num = pagination_num.select_one("ul > li:nth-last-child(2)")

        if pagination_num:
            pagination_num = pagination_num["onclick"]
            # We match page={number} from the link and then extract the number
            regex = re.compile(r"page=\d+")
            pagination_num = regex.findall(pagination_num)[0].split("=")[1]
            pagination_num = int(pagination_num)
        else:
            pagination_num = 1

        futures = [
            self.executor.submit(self.get_soup, f"{self.novel_url}?page={i}")
            for i in range(1, pagination_num + 1)
        ]
        page_soups = [f.result() for f in futures]

        possible_title = page_soups[0].select_one("h2.text-2xl")
        assert possible_title, "No novel title"
        text_sm = possible_title.select_one("span")
        if text_sm:
            text_sm.extract()
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        author = page_soups[0].select("p:nth-child(4) > span.capitalize")
        if len(author) == 2:
            self.novel_author = author[0].text + " (" + author[1].text + ")"
        elif author[0].text != "-":
            self.novel_author = author[0].text
        logger.info("Novel author: %s", self.novel_author)

        self.novel_cover = self.absolute_url(
            page_soups[0].select_one("div.relative > img")["src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        # [sp.select("div#chapters-list a") for sp in soup]
        # flattened ->
        # [a for sp in soup for a in sp.select("div#chapters-list a")])
        for element in reversed(
            [a for soup in page_soups for a in soup.select("div#chapters-list a")]
        ):
            ch_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": ch_id,
                    "volume": vol_id,
                    "title": element.select_one("div div span").text,
                    "url": self.absolute_url(element["href"]),
                }
            )
        logger.debug(
            "%d chapters and %d volumes found", len(self.chapters), len(self.volumes)
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.mx-auto.max-w-3xl")

        return str(contents)
