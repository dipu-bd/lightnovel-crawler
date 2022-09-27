# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://www.novelupdates.cc/search/%s/1"


class NovelUpdatesCC(Crawler):
    base_url = [
        "https://www.novelupdates.cc/",
    ]

    def search_novel(self, query):
        query = quote(query.lower())
        soup = self.get_soup(search_url % query)

        results = []
        for li in soup.select(".result-list .list-item"):
            a = li.select_one("a.book-name")
            for bad in a.select("font"):
                bad.extract()
            catalog = li.select_one(".book-catalog").text.strip()
            votes = li.select_one(".star-suite .score").text.strip()
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | Rating: %s" % (catalog, votes),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("div.book-name")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = soup.select_one("div.author span.name").text.strip()
        logger.info("Novel author: %s", self.novel_author)

        possible_image = soup.select_one("div.book-img img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select("ul.chapter-list a")

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.select_one("p.chapter-name").text.strip()
                    or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        chapter["title"] = soup.select_one("h1.chapter-title").text.strip()

        self.cleaner.bad_text_regex = set(
            [
                r"^translat(ed by|or)",
                r"(volume|chapter) .?\d+",
            ]
        )
        body_parts = soup.select_one("div.chapter-entity")

        return self.cleaner.extract_contents(body_parts)
