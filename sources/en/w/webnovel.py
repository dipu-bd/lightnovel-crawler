# -*- coding: utf-8 -*-
import logging
import re
from functools import cached_property
from time import time
from typing import Iterable
from urllib.parse import urlencode, urlparse

from lncrawl.core import BrowserTemplate, Chapter, Novel, PageSoup, SearchResult, Volume
from lncrawl.exceptions import FallbackToBrowser, LNException

logger = logging.getLogger(__name__)


class WebnovelCrawler(BrowserTemplate):
    base_url = [
        "https://m.webnovel.com/",
        "https://www.webnovel.com/",
    ]

    def initialize(self) -> None:
        self.scraper.origin = "https://www.webnovel.com/"
        bad_text = [
            r"(\<pirate\>(.*?)\<\/pirate\>)"
            r"(Find authorized novels in Webnovel(.*)for visiting\.)",
        ]
        self.re_cleaner = re.compile("|".join(bad_text), re.M)
        self.__dict__.pop("csrf", None)

    @cached_property
    def csrf(self):
        self.scraper.get(f"{self.scraper.origin}stories/novel")
        return self.scraper.cookies.get("_csrfToken") or ""

    def search(self, query: str) -> Iterable[SearchResult]:
        try:
            params = {
                "_csrfToken": self.csrf,
                "pageIndex": 1,
                "encryptType": 3,
                "_fsae": 0,
                "keywords": query,
            }
            data = self.scraper.get_json(
                f"{self.scraper.origin}go/pcm/search/result?{urlencode(params)}"
            )
            for book in data["data"]["bookInfo"]["bookItems"]:
                yield SearchResult(
                    title=book["bookName"],
                    url=f"{self.scraper.origin}book/{book['bookId']}",
                    info="%(categoryName)s | Score: %(totalScore)s" % book,
                )
        except Exception:
            params = {"keywords": query}
            self.visit(f"{self.scraper.origin}search?{urlencode(params)}")
            for li in self.browser.soup.select(".search-result-container li"):
                a = li.find("a[href]")
                info = li.find(".g_star_num small")
                if a:
                    yield SearchResult(
                        url=self.absolute_url(a.get("href")),
                        title=str(a.get("data-bookname") or ""),
                        info=info.get_text(strip=True) if info else "",
                    )

    def read_novel(self, novel: Novel) -> None:
        if "_" not in novel.url:
            ids = re.findall(r"/book/(\d+)", novel.url)
            if not ids:
                raise LNException("Invalid novel URL")
            novel.novel_id = ids[0]
        else:
            novel.novel_id = novel.url.split("_")[1]

        data = self.scraper.get_json(
            f"{self.scraper.origin}go/pcm/chapter/getContent"
            + f"?_csrfToken={self.csrf}&bookId={novel.novel_id}&chapterId=0"
            + "&encryptType=3&_fsae=0"
        )

        if "data" not in data:
            raise LNException("Get content failed")
        data = data["data"]

        if "bookInfo" not in data:
            raise LNException("Get book info failed")
        book_info = data["bookInfo"]

        if "bookName" not in book_info:
            raise LNException("Get book title failed")
        novel.title = book_info["bookName"]

        novel.cover_url = self.absolute_url(
            f"//book-pic.webnovel.com/bookcover/{novel.novel_id}"
            + f"?coverUpdateTime{int(1000 * time())}&imageMogr2/thumbnail/600x"
        )

        if "authorName" in book_info:
            novel.author = book_info["authorName"]
        elif "authorItems" in book_info:
            novel.author = ", ".join(
                [x.get("name") for x in book_info["authorItems"] if x.get("name")]
            )

        # To get the chapter list catalog
        soup = self.scraper.get_soup(f"{novel.url.strip('/')}/catalog")
        self.parse_chapter_catalog(soup, novel)

    def parse_chapter_catalog(self, soup: PageSoup, novel: Novel) -> None:
        novel.volumes = []
        novel.chapters = []
        for div in soup.select(".j_catalog_list .volume-item"):
            vol = Volume(
                id=len(novel.volumes) + 1,
                title=div.find("h4").text,
            )
            novel.volumes.append(vol)

            for a in div.select("ol > li > a[href]"):
                cid = a.parent.get("data-report-cid")
                if not cid:
                    continue  # skip chapter without id
                if a.select_one("svg._icon"):
                    continue  # skiplocked chapter
                chapter = Chapter(
                    id=len(novel.chapters) + 1,
                    title=str(a.get("title") or ""),
                    url=self.absolute_url(a.get("href")),
                    volume=vol.id,
                    novel_id=novel.novel_id,
                    chapter_id=cid,
                )
                novel.chapters.append(chapter)

    def parse_chapter_catalog_in_browser(self, soup: PageSoup, novel: Novel) -> None:
        novel.volumes = []
        novel.chapters = []
        for div in soup.select(".j_catalog_list .volume-item"):
            vol = Volume(
                id=len(novel.volumes) + 1,
                title=div.find("h4").text,
            )
            novel.volumes.append(vol)

            for li in div.select("li"):
                a = li.find("a[href]")
                cid = li.get("data-report-cid")
                if not a or not cid:
                    continue
                chap = Chapter(
                    id=len(novel.chapters) + 1,
                    title=str(a.get("title") or ""),
                    url=self.absolute_url(a.get("href")),
                    volume=vol.id,
                    novel_id=novel.novel_id,
                    chapter_id=cid,
                )
                novel.chapters.append(chap)

    def download_chapter(self, chapter: Chapter) -> None:
        try:
            params = {
                "encryptType": 3,
                "_fsae": 0,
                "_csrfToken": self.csrf,
                "bookId": chapter.novel_id,
                "chapterId": chapter.chapter_id,
            }
            data = self.scraper.get_json(
                f"{self.scraper.origin}go/pcm/chapter/getContent?{urlencode(params)}"
            )

            if "data" not in data:
                raise FallbackToBrowser()
            data = data["data"]

            if "chapterInfo" not in data:
                raise FallbackToBrowser()
            chapter_info = data["chapterInfo"]

            chapter.title = chapter_info["chapterName"]
            if "content" in chapter_info:
                chapter.body = self._format_content(chapter_info["content"])
            elif "contents" in chapter_info:
                body = [
                    self._format_content(x["content"])
                    for x in chapter_info["contents"]
                    if "content" in x
                ]
                chapter.body = "".join([x for x in body if x.strip()])

            if not chapter.body:
                raise FallbackToBrowser()

        except Exception:
            path = urlparse(chapter.url).path.strip("/")
            soup = self.scraper.get_soup(f"{self.scraper.origin}{path}")
            contents = soup.select(f".j_chapter_{chapter.chapter_id} .cha-paragraph p")
            body = [self._format_content(p.text) for p in contents]
            chapter.body = "".join(filter(None, body))

    def _format_content(self, text: str):
        if ("<p>" not in text) or ("</p>" not in text):
            text = "".join(text.split("\r"))
            text = "&lt;".join(text.split("<"))
            text = "&gt;".join(text.split(">"))
            text = "</p><p>".join([x.strip() for x in text.split("\n") if x.strip()])
        text = self.re_cleaner.sub("", f"<p>{text}</p>")
        return text.strip()
