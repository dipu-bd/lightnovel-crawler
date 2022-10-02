# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "%s/?s=%s"


class TamagoTlCrawler(Crawler):
    base_url = [
        "https://tamagotl.com/",
    ]
    has_mtl = True

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % (self.home_url, query))

        results = []
        for article in soup.select(".listupd article.bs"):
            a = article.select_one("a.tip")
            if not isinstance(a, Tag):
                continue
            results.append(
                {
                    "title": a.select_one("span.ntitle").text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        if possible_title:
            self.novel_title = possible_title.get_text()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".thumbook img.wp-post-image")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        for span in soup.select(".spe span"):
            text = span.text.strip()
            if text.startswith("Author"):
                authors = span.select("a")
                if len(authors) == 2:
                    self.novel_author = authors[0].text + " (" + authors[1].text + ")"
                elif len(authors) == 1:
                    self.novel_author = authors[0].text
                break

        logger.info("Novel author: %s", self.novel_author)

        for a in reversed(soup.select(".eplisterfull a")):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.select_one(".epl-title").text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div.entry-content")
        return self.cleaner.extract_contents(contents)
