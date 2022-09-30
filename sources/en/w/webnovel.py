# -*- coding: utf-8 -*-
import logging
import re
import time
from urllib.parse import quote_plus

from lncrawl.core.crawler import Crawler
from lncrawl.models.chapter import Chapter

logger = logging.getLogger(__name__)


class WebnovelCrawler(Crawler):
    base_url = [
        "https://m.webnovel.com/",
        "https://www.webnovel.com/",
    ]

    def initialize(self) -> None:
        self.init_executor(1)
        self.home_url = "https://www.webnovel.com/"
        self.re_cleaner = re.compile(
            "|".join(
                [
                    r"(\<pirate\>(.*?)\<\/pirate\>)"
                    r"(Find authorized novels in Webnovel(.*)for visiting\.)",
                ]
            ),
            re.MULTILINE,
        )

    def get_csrf(self):
        logger.info("Getting CSRF Token")
        self.get_response(self.home_url)
        self.csrf = self.cookies["_csrfToken"]
        logger.debug("CSRF Token = %s", self.csrf)

    def search_novel(self, query):
        self.get_csrf()
        query = quote_plus(str(query).lower())
        data = self.get_json(
            f"{self.home_url}go/pcm/search/result"
            + f"?_csrfToken={self.csrf}&pageIndex=1&encryptType=3&_fsae=0&keywords={query}"
        )

        results = []
        for book in data["data"]["bookInfo"]["bookItems"]:
            results.append(
                {
                    "title": book["bookName"],
                    "url": f"{self.home_url}book/{book['bookId']}",
                    "info": "%(categoryName)s | Score: %(totalScore)s" % book,
                }
            )
        return results

    def read_novel_info(self):
        self.get_csrf()
        url = self.novel_url
        if "_" not in url:
            ids = re.findall(r"/book/(\d+)", url)
            assert ids, "Please enter a correct novel URL"
            self.novel_id = ids[0]
        else:
            self.novel_id = url.split("_")[1]
        logger.info("Novel Id: %s", self.novel_id)

        response = self.get_response(
            f"{self.home_url}go/pcm/chapter/getContent"
            + f"?_csrfToken={self.csrf}&bookId={self.novel_id}&chapterId=0"
            + "&encryptType=3&_fsae=0"
        )
        data = response.json()
        logger.debug("Book Response:\n%s", data)

        assert "data" in data, "Data not found"
        data = data["data"]

        assert "bookInfo" in data, "Book info not found"
        book_info = data["bookInfo"]

        assert "bookName" in book_info, "Book name not found"
        self.novel_title = book_info["bookName"]

        self.novel_cover = (
            f"{self.origin.scheme}://img.webnovel.com/bookcover/{self.novel_id}/600/600.jpg"
            + f"?coverUpdateTime{int(1000 * time.time())}&imageMogr2/quality/40"
        )

        if "authorName" in book_info:
            self.novel_author = book_info["authorName"]
        elif "authorItems" in book_info:
            self.novel_author = ", ".join(
                [x.get("name") for x in book_info["authorItems"] if x.get("name")]
            )

        self.chapter_ids = {}
        if "firstChapterId" in book_info:
            self.chapter_ids[1] = book_info["firstChapterId"]
        elif "chapterId" in data.get("chapterInfo"):
            self.chapter_ids[1] = data["chapterInfo"]["chapterId"]
        else:
            raise Exception("First chapter id not found")

        assert "totalChapterNum" in book_info, "Total chapter number not found"
        for i in range(book_info["totalChapterNum"]):
            self.chapters.append(Chapter(id=i + 1))

    def download_chapter_body(self, chapter: Chapter):
        chapter_id = self.chapter_ids.get(chapter.id)
        assert chapter_id, "Previous chapter id not available"

        response = self.get_response(
            f"{self.home_url}go/pcm/chapter/getContent"
            + f"?_csrfToken={self.csrf}&bookId={self.novel_id}&chapterId={chapter_id}"
            + "&encryptType=3&_fsae=0"
        )
        data = response.json()
        logger.debug("Chapter Response:\n%s", data)

        assert "data" in data, "Data not found"
        data = data["data"]

        assert "chapterInfo" in data, "Chapter Info not found"
        chapter_info = data["chapterInfo"]

        chapter.title = chapter_info["chapterName"] or f"Chapter #{chapter.id}"
        self.chapter_ids[chapter.id + 1] = chapter_info["nextChapterId"]

        if "content" in chapter_info:
            return self._format_content(chapter_info["content"])

        if "contents" in chapter_info:
            body = [
                self._format_content(x["content"])
                for x in chapter_info["contents"]
                if "content" in x
            ]
            return "".join([x for x in body if x.strip()])

    def _format_content(self, text: str):
        if ("<p>" not in text) or ("</p>" not in text):
            text = "".join(text.split("\r"))
            text = "&lt;".join(text.split("<"))
            text = "&gt;".join(text.split(">"))
            text = [x.strip() for x in text.split("\n") if x.strip()]
            text = "<p>" + "</p><p>".join(text) + "</p>"
        text = self.re_cleaner.sub("", text)
        return text.strip()
