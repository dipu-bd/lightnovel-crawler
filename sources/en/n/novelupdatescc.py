# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote

from lncrawl.core.crawler import Crawler
from lncrawl.models.chapter import Chapter

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

        possible_title = soup.select_one(".book-name")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_author = soup.select_one(".person-info .author .name")
        if possible_author:
            self.novel_author = possible_author.text.strip()
        logger.info("Novel author: %s", self.novel_author)

        possible_image = soup.select_one(".book-img img[src]")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        for a in soup.select("ul.chapter-list a[href]"):
            self.chapters.append(
                Chapter(
                    id=len(self.chapters) + 1,
                    title=a.text.strip(),
                    url=self.absolute_url(a["href"]),
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.select_one("#chapter-entity")
        return self.cleaner.extract_contents(content)
