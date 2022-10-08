# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class WuxiaCoCrawler(Crawler):
    base_url = [
        "https://www.wuxiaworld.co/",
        "https://m.wuxiaworld.co/",
    ]

    def initialize(self):
        self.home_url = "https://m.wuxiaworld.co/"
        self.init_executor(1)
        self.cleaner.bad_text_regex.update(
            [
                r"^translat(ed by|or)",
                r"(volume|chapter) .?\d+",
            ]
        )

    def search_novel(self, query):
        soup = self.get_soup(f"{self.home_url}search/{quote(query)}/1")
        results = []
        for li in soup.select("ul.result-list li.list-item"):
            a = li.select_one("a.book-name")["href"]
            author = li.select_one("a.book-name font").text
            title = li.select_one("a.book-name").text.replace(author, "")
            results.append(
                {
                    "title": title,
                    "url": self.absolute_url(a),
                    "info": f"Author: {author}",
                }
            )
        return results

    def read_novel_info(self):
        url = self.novel_url.replace("https://www", "https://m")
        soup = self.get_soup(url)

        possible_title = soup.select_one("div.book-name")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()

        possible_author = soup.select_one("div.author span.name")
        if possible_author:
            self.novel_author = possible_author.text.strip()

        possible_image = soup.select_one("div.book-img img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])

        for a in soup.select("ul.chapter-list a.chapter-item"):
            chap_id = len(self.chapters) + 1
            possible_name = a.select_one(".chapter-name")
            self.chapters.append(
                {
                    "id": chap_id,
                    "url": self.absolute_url(a["href"]),
                    "title": possible_name.text if possible_name else "",
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        possible_title = soup.select_one("h1.chapter-title")
        if possible_title:
            chapter["title"] = possible_title.text.strip()

        body_parts = soup.select_one("div.chapter-entity")
        return self.cleaner.extract_contents(body_parts)
