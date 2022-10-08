# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class BlackboxTL(Crawler):
    base_url = "https://www.blackbox-tl.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        image = soup.select_one(".entry-content img")
        self.novel_cover = self.absolute_url(image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        for p in soup.select("div.entry-content p"):
            possible_author = re.sub(r"[\(\s\n\)]+", " ", p.text, re.M).strip()
            if possible_author.startswith("Author:"):
                possible_author = re.sub("Author:", "", possible_author)
                self.novel_author = possible_author.strip()
                break
        logger.info("Novel author: %s", self.novel_author)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select('div.entry-content p a[href*="blackbox-tl.com/novels/"]')

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
        body_parts = soup.select_one("div.entry-content")

        # NOTE: self.cleaner cannot be used as it removes chapter text because of site formatting.
        for bad_css in body_parts.select(".abh_box, hr"):
            bad_css.extract()

        for toc in body_parts.select("p"):
            for text in [
                "Table of Contents",
                "Next Chapter →",
                "← Previous Chapter",
            ]:
                if text in toc.text:
                    toc.extract()

        return str(body_parts)
