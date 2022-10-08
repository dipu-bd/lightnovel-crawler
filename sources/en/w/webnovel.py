# -*- coding: utf-8 -*-
import logging
import re
from time import time
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from lncrawl.core.exeptions import FallbackToBrowser
from lncrawl.models import Chapter, SearchResult
from lncrawl.models.volume import Volume
from lncrawl.templates.browser.basic import BasicBrowserTemplate
from lncrawl.webdriver.elements import By

logger = logging.getLogger(__name__)


class WebnovelCrawler(BasicBrowserTemplate):
    base_url = [
        "https://m.webnovel.com/",
        "https://www.webnovel.com/",
    ]

    def initialize(self) -> None:
        self.headless = True
        self.home_url = "https://www.webnovel.com/"
        bad_text = [
            r"(\<pirate\>(.*?)\<\/pirate\>)"
            r"(Find authorized novels in Webnovel(.*)for visiting\.)",
        ]
        self.re_cleaner = re.compile("|".join(bad_text), re.M)

    def get_csrf(self):
        logger.info("Getting CSRF Token")
        self.get_response(self.home_url)
        self.csrf = self.cookies["_csrfToken"]
        logger.debug("CSRF Token = %s", self.csrf)

    def search_novel_in_scraper(self, query: str):
        self.get_csrf()
        params = {
            "_csrfToken": self.csrf,
            "pageIndex": 1,
            "encryptType": 3,
            "_fsae": 0,
            "keywords": query,
        }
        data = self.get_json(f"{self.home_url}go/pcm/search/result?{urlencode(params)}")
        for book in data["data"]["bookInfo"]["bookItems"]:
            yield SearchResult(
                title=book["bookName"],
                url=f"{self.home_url}book/{book['bookId']}",
                info="%(categoryName)s | Score: %(totalScore)s" % book,
            )

    def search_novel_in_browser(self, query: str):
        params = {"keywords": query}
        self.visit(f"{self.home_url}search?{urlencode(params)}")
        self.last_soup_url = self.browser.current_url
        for li in self.browser.soup.select(".search-result-container li"):
            a = li.find("a")
            yield SearchResult(
                url=self.absolute_url(a.get("href")),
                title=a.get("data-bookname"),
                info=li.find(".g_star_num small").text.strip(),
            )

    def read_novel_info_in_scraper(self):
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
            + f"?coverUpdateTime{int(1000 * time())}&imageMogr2/quality/40"
        )

        if "authorName" in book_info:
            self.novel_author = book_info["authorName"]
        elif "authorItems" in book_info:
            self.novel_author = ", ".join(
                [x.get("name") for x in book_info["authorItems"] if x.get("name")]
            )

        # To get the chapter list catalog
        soup = self.get_soup(f"{self.novel_url.strip('/')}/catalog")
        self.parse_chapter_catalog(soup)
        if not self.chapters:
            raise FallbackToBrowser()

    def read_novel_info_in_browser(self) -> None:
        self.visit(f"{self.novel_url.strip('/')}/catalog")
        self.last_soup_url = self.browser.current_url
        self.browser.wait(".j_catalog_list")
        self.parse_chapter_catalog(self.browser.soup)

    def parse_chapter_catalog(self, soup: BeautifulSoup) -> None:
        for div in soup.select(".j_catalog_list .volume-item"):
            vol = Volume(
                id=len(self.volumes) + 1,
                title=div.find("h4").text.strip(),
            )
            self.volumes.append(vol)
            for li in div.select("li"):
                a = li.find("a")
                chap = Chapter(
                    id=len(self.chapters) + 1,
                    volume=vol.id,
                    title=a.get("title"),
                    cid=li.get("data-report-cid"),
                    url=self.absolute_url(a.get("href")),
                )
                self.chapters.append(chap)

    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        self.visit(chapter.url)
        self.browser.wait(f"j_chapter_{chapter.cid}", By.CLASS_NAME)

        body = ""
        for p in self.browser.soup.select(f".j_chapter_{chapter.cid} .cha-paragraph p"):
            body += str(p)
        return body

    def download_chapter_body_in_scraper(self, chapter: Chapter) -> str:
        logger.info("Chapter Id: %s", chapter.cid)

        response = self.get_response(
            f"{self.home_url}go/pcm/chapter/getContent?encryptType=3&_fsae=0"
            + f"&_csrfToken={self.csrf}&bookId={self.novel_id}&chapterId={chapter.cid}"
        )
        data = response.json()
        logger.debug("Chapter Response:\n%s", data)

        assert "data" in data, "Data not found"
        data = data["data"]

        assert "chapterInfo" in data, "Chapter Info not found"
        chapter_info = data["chapterInfo"]

        chapter.title = chapter_info["chapterName"] or f"Chapter #{chapter.id}"

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
