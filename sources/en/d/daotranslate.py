# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://daotranslate.us/?s=%s"


class DaoTranslateCrawler(Crawler):
    base_url = ["https://daotranslate.com/", "https://daotranslate.us/"]
    has_mtl = True

    def initialize(self):
        self.init_executor(ratelimit=1.1)

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select("article.maindet")[:10]:
            a = tab.select_one("h2 a")
            if not isinstance(a, Tag):
                continue

            info = []
            latest = tab.select_one(".mdinfodet .nchapter a")
            if isinstance(latest, Tag):
                info.append(latest.text.strip())

            votes = tab.select_one(".mdinfodet .mdminf")
            if isinstance(votes, Tag):
                info.append("Rating: " + votes.text.strip())

            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": " | ".join(info),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.infox h1').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one(".thumbook .thumb img")
        if isinstance(possible_image, Tag):
            self.novel_cover = possible_image["data-src"]
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select_one(
            ".info-content .spe span:nth-child(3) a"
        )
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info("Novel author: %s", self.novel_author)

        possible_synopsis = soup.select(".entry-content p")
        if possible_synopsis:
            self.novel_synopsis = "".join([str(p) for p in possible_synopsis])
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        for a in reversed(soup.select(".eplisterfull ul li a")):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.select_one('.epl-title').text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select(".epcontent.entry-content p")
        return "".join([str(p) for p in contents])
