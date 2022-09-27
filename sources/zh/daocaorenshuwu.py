# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Daocaorenshuwu(Crawler):
    base_url = [
        "https://www.daocaorenshuwu.com/",
    ]

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".container .book-info h1.book-name")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = soup.select(".container .media-body .row div")[
            0
        ].text.strip()
        logger.info("Novel author: %s", self.novel_author)

        possible_image = soup.select_one(".container .media-left a img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        # Extract volume-wise ch
        # apter entries
        chapters = soup.select("#all-chapter a")

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
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select(".cont-text > p")
        contents = [str(p) for p in contents if p.text.strip()]
        return "".join(contents)
