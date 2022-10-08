# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

NOVEL_SEARCH = "http://fullnovel.live/search/%s"


class FullnovelLiveCrawler(Crawler):
    base_url = "http://fullnovel.live/"

    def search_novel(self, query):
        """Gets a list of (title, url) matching the given query"""
        results = []
        soup = self.get_soup(NOVEL_SEARCH % query)
        for grid in soup.select(".grid .v-grid"):
            a = grid.select_one("h4 a")
            info = grid.select_one(".info-line a").text
            results.append(
                {
                    "title": str(a["title"] or a.text).strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": info,
                }
            )
        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        possible_title = soup.select_one(".info h1.title a")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        possible_image = soup.select_one(".info .image img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])

        chapters = soup.select(".scroll-eps a")
        chapters.reverse()

        vols = set([])
        for x in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(x["href"]),
                    "title": x.text.strip() or ("Chapter %d" % chap_id),
                }
            )

        self.volumes = [{"id": x} for x in vols]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".page .divContent")
        return self.cleaner.extract_contents(contents)
