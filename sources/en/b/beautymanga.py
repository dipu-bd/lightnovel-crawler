# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class BeautymangaCrawler(Crawler):
    has_manga = True
    base_url = [
        "https://beautymanga.com/",
    ]

    def search_novel(self, query):
        search_url = f"{self.home_url}search-autocomplete?action=wp-manga-search-manga&title={quote_plus(query)}"
        data = self.get_json(search_url)
        results = []
        for item in data["data"]:
            results.append(
                {"title": item["title"], "url": self.absolute_url(item["url"])}
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_id = soup.select_one("#manga-chapters-holder[data-id]")
        assert possible_id, "No chapter id found"
        self.novel_id = int(possible_id["data-id"])

        possible_title = soup.select_one(".post-title h1")
        assert possible_title, "Could not find title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".summary_image img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = ", ".join(
            [a.text for a in soup.select('.author-content a[href="/author/"]')]
        )
        logger.info("Novel author: %s", self.novel_author)

        soup = self.get_soup(
            f"{self.home_url}ajax-list-chapter?mangaID={self.novel_id}"
        )
        for a in reversed(soup.select(".wp-manga-chapter a")):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text,
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        arraydata = soup.select_one("#arraydata")
        if arraydata:
            urls = arraydata.text.strip().split(",")
            return "".join([f'<img src="{src}" />' for src in urls if src])
        contents = soup.select_one(".reading-content")
        return self.cleaner.extract_contents(contents)
