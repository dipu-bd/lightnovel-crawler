# -*- coding: utf-8 -*-

import logging
from lncrawl.core.crawler import Crawler
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

search_url = "https://www.wuxia.city/search?q=%s"


class WuxiaCityCrawler(Crawler):
    base_url = [
        "https://wuxia.city",
    ]

    # This source offers no manga/manhua/manhwa.
    has_manga = False

    # Set True if this source contains machine translations.
    has_mtl = True

    def search_novel(self, query):
        query = quote_plus(str(query).lower())
        soup = self.get_soup(search_url % query)
        entries = [
            (
                e.find("div", class_="book-caption"),
                e.find("p", class_="book-genres").a.text,
                e.find("span", class_="star").get("style").split(" ")[1],
            )
            for e in soup.find_all("li", class_="section-item")
        ]
        return [
            {
                "title": e[0].a.h4.text,
                "url": f'{self.home_url.strip("/")}{e[0].a.get("href")}',
                "info": f"{e[1]} | Score: {e[2]}",
            }
            for e in entries
        ]

    def read_novel_info(self):
        soup = self.get_soup(f"{self.novel_url}/table-of-contents")

        self.novel_title = soup.find("h1", class_="book-name").text
        self.novel_author = soup.find("dl", class_="author").dd.text
        self.novel_cover = soup.find("div", class_="book-img").img.get("src")

        vol_id = 0
        self.volumes.append({"id": vol_id})
        chapterItems = soup.find("ul", class_="chapters").find_all(
            "li", class_="oneline"
        )
        for chapter in chapterItems:
            self.chapters.append(
                {
                    "id": int(chapter.find("span", class_="chapter-num").text),
                    "volume": vol_id,
                    "url": f'{self.home_url.strip("/")}{chapter.a.get("href")}',
                    "title": chapter.a.p.text,
                    "hash": chapter.a.get("href").split("/")[-1],
                }
            )
        self.chapters.sort(key=lambda c: c["id"])

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        return self.cleaner.extract_contents(soup.find("div", class_="chapter-content"))
