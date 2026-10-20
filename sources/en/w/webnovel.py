# -*- coding: utf-8 -*-
from functools import cached_property
import logging
import re
from time import time
from typing import Iterable
from urllib.parse import urlencode, urlparse

from lncrawl.core import (
    Chapter,
    Novel,
    PageSoup,
    SearchResult,
    SoupTemplate,
    Volume,
)
from lncrawl.exceptions import LNException

try:
    from lncrawl.exceptions import ChapterLockedError
except ImportError:
    # Sources update independently, so keep loading on older app versions.
    from lncrawl.exceptions import LNException as ChapterLockedError

logger = logging.getLogger(__name__)


class _LockedChapter(ChapterLockedError):
    def __init__(self, chapter: Chapter) -> None:
        self.chapter_number = chapter.id
        label: str = f"Chapter {chapter.id}"
        if chapter.title and chapter.title.casefold() != label.casefold():
            label = f"{label} ({chapter.title})"
        super().__init__(f"{label} is locked on Webnovel; its preview is not a complete chapter")


class WebnovelCrawler(SoupTemplate):
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
            logger.warning("Failed to search %s", self.scraper.origin, exc_info=True)

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
            raise LNException("Invalid JSON: no data")
        data = data["data"]

        if "bookInfo" not in data:
            raise LNException("Invalid JSON: no bookInfo")
        book_info = data["bookInfo"]

        if "bookName" not in book_info:
            raise LNException("Invalid JSON: no bookName")
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
                # Lock icons describe access, not catalog membership. Keep the full order.
                chapter = Chapter(
                    id=len(novel.chapters) + 1,
                    title=str(a.get("title") or ""),
                    url=self.absolute_url(a.get("href")),
                    volume=vol.id,
                    novel_id=novel.novel_id,
                    chapter_id=cid,
                )
                novel.chapters.append(chapter)

    def download_chapter(self, chapter: Chapter) -> None:
        chapter.body = None
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
                raise LNException("Invalid JSON: no data")
            data = data["data"]

            if "chapterInfo" not in data:
                raise LNException("Invalid JSON: no chapterInfo")
            chapter_info = data["chapterInfo"]

            # The API returns preview paragraphs even when chapter access is denied.
            if chapter_info.get("isAuth") in (0, "0"):
                raise _LockedChapter(chapter)

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
                raise LNException("Invalid JSON: no chapter.body")

        except _LockedChapter:
            # The HTML contains the same preview, not an alternative way to access it.
            raise
        except Exception:
            self._download_chapter_html(chapter)

    def _download_chapter_html(self, chapter: Chapter) -> None:
        path: str = urlparse(chapter.url).path.strip("/")
        soup: PageSoup = self.scraper.get_soup(f"{self.scraper.origin}{path}")
        content: PageSoup = soup.select_one(f".j_chapter_{chapter.chapter_id}")
        if content.get("data-islock") == "1":
            raise _LockedChapter(chapter)
        contents: list[PageSoup] = content.select(".cha-paragraph p")
        body: list[str] = [self._format_content(p.text) for p in contents]
        chapter.body = "".join(filter(None, body))

    def _format_content(self, text: str) -> str:
        if ("<p>" not in text) or ("</p>" not in text):
            text = "".join(text.split("\r"))
            text = "&lt;".join(text.split("<"))
            text = "&gt;".join(text.split(">"))
            text = "</p><p>".join([x.strip() for x in text.split("\n") if x.strip()])
        text = self.re_cleaner.sub("", f"<p>{text}</p>")
        return text.strip()
