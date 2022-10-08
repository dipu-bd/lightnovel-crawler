# -*- coding: utf-8 -*-
import logging
from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://mostnovel.com/?s=%s&post_type=wp-manga"


class MostNovel(Crawler):
    base_url = "https://mostnovel.com/"

    def initialize(self):
        self.cleaner.bad_css.update(
            [
                "div.skiptranslate",
            ]
        )

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h3 a")
            latest = tab.select_one(".latest-chap .chapter a").text
            votes = tab.select_one(".rating .total_votes").text
            results.append(
                {
                    "title": a.text.rsplit(" ", 1)[0].strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | Rating: %s" % (latest, votes),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        image = soup.select_one(".summary_image a img")
        assert isinstance(image, Tag), "No title found"

        self.novel_title = image["alt"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(image["data-src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="manga-author"]')
            ]
        )
        logger.info("%s", self.novel_author)

        chapter_list_url = self.absolute_url("ajax/chapters", self.novel_url)
        soup = self.post_soup(chapter_list_url, headers={"accept": "*/*"})
        for a in reversed(
            soup.select('.wp-manga-chapter a[href*="/manga"]')
        ):  # This stops it from trying to download locked premium chapters.
            for span in a.findAll("span"):  # Removes time and date from chapter title.
                span.extract()
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".text-left")
        return self.cleaner.extract_contents(contents)
