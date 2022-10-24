# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "%s/?s=%s&post_type=wp-manga"


class ListNovelCrawler(Crawler):
    has_mtl = True
    base_url = [
        "https://mixednovel.net/",
    ]

    def initialize(self):
        self.init_executor(1)

    def search_novel(self, query):
        query = quote_plus(query.lower())
        soup = self.get_soup(search_url % (self.home_url.strip("/"), query))
        results = []
        for tab in soup.select(".c-tabs-item .c-tabs-item__content"):
            a = tab.select_one(".post-title a")
            alternative = tab.select_one(".mg_alternative .summary-content").text.strip()
            author = tab.select_one(".mg_author .summary-content a").text.strip()
            results.append(
                {
                    "title": a.text,
                    "url": self.absolute_url(a["href"]),
                    "info": "Alternative title(s): %s | Author(s): %s" % (alternative, author),
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = ", ".join(
            [a.text.strip() for a in soup.select('.summary-content a[href*="/novel-author/"]')]
        )
        logger.info("%s", self.novel_author)

        possible_image = soup.select_one(".summary_image img")
        if isinstance(possible_image, Tag):
            urls = possible_image['src']
            self.novel_cover = self.absolute_url(urls) if urls else None
        logger.info("Novel cover: %s", self.novel_cover)

        chapter_url = "%s/ajax/chapters/"
        chapter_soup = self.post_soup(chapter_url % (self.novel_url.strip("/")))
        all_chapter_soup = chapter_soup.select(".main .wp-manga-chapter")
        for chapter in all_chapter_soup:
            chap_id = len(all_chapter_soup) - len(self.chapters)
            a = chapter.select_one("a")
            self.chapters.append(
                {
                    "id": chap_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select(".reading-content .text-left")
        return "".join([str(p) for p in contents])
