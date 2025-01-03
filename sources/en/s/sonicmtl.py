# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class SonicMTLCrawler(Crawler):
    has_mtl = True
    base_url = [
        "https://www.sonicmtl.com/",
    ]

    def initialize(self):
        self.cleaner.bad_css.update({
            '.ad',
            '.c-ads',
            '.custom-code',
            '.body-top-ads',
            '.before-content-ad',
            '.autors-widget',
        })
        return super().initialize()

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".summary_image img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = ', '.join([
            a.text.strip()
            for a in soup.select(".author-content a")
        ])
        logger.info("Novel author: %s", self.novel_author)

        self.novel_tags = [
            a.text.strip()
            for a in soup.select('.genres-content a[rel="tag"]')
        ]

        possible_summary = soup.select_one(".description-summary a")
        if possible_summary:
            self.novel_synopsis = self.cleaner.extract_contents(possible_summary)

        soup = self.post_soup(
            f"{self.novel_url}ajax/chapters/"
        )
        for a in reversed(soup.select(".wp-manga-chapter a")):
            chap_id = len(self.chapters) + 1
            self.chapters.append(
                {
                    "id": chap_id,
                    "title": a.text,
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".entry-content .reading-content .text-left")
        return self.cleaner.extract_contents(contents)
