# -*- coding: utf-8 -*-
import logging
from bs4 import Tag
from urllib.parse import quote
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "%s/book/searchByPageInShelf?curr=1&limit=10&keyword=%s"
fetch_chapter_list_url = "%s/book/queryIndexList?bookId=%s&curr=1&limit=50000"
fetch_chapter_body_url = (
    "%s/book/queryBookIndexContent?bookId=%s&bookIndexId=%s&autoUnlock=false"
)


class NovelHiCrawler(Crawler):
    base_url = [
        "https://novelhi.com/",
    ]

    def search_novel(self, query):
        data = self.get_json(search_url % (self.home_url, quote(query)))

        results = []
        for item in data["data"]["list"]:
            results.append(
                {
                    "title": item["bookName"],
                    "url": "%s/s/%s" % (self.home_url, item["simpleName"]),
                    "info": "Latest: %s (%s)"
                    % (item["lastIndexName"], item["lastIndexUpdateTime"]),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_book_id = soup.select_one("input#bookId")
        assert isinstance(possible_book_id, Tag), "No book id"
        self.novel_id = possible_book_id["value"]

        possible_image = soup.select_one("a.book_cover img.cover")
        assert isinstance(possible_image, Tag), "No novel title"

        self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_title = possible_image["alt"]
        logger.info("Novel title: %s", self.novel_title)

        for item in soup.select(".book_info ul.list span.item"):
            item.text.startswith("Author")
            possible_author = item.select_one("em")
            if isinstance(possible_author, Tag):
                self.novel_author = possible_author.text
            break
        logger.info("Novel author: %s", self.novel_author)

        data = self.get_json(fetch_chapter_list_url % (self.home_url, self.novel_id))
        for item in reversed(data["data"]["list"]):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": item["indexName"],
                    "url": "%s/%s" % (self.novel_url.strip("/"), item["indexNum"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        paras = soup.select("#showReading sent")
        return "".join(["<p>%s</p>" % p.text for p in paras])
        # assert isinstance(contents, Tag), 'No contents'
        # return self.cleaner.extract_contents(contents)
