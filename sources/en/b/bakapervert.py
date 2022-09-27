# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class BakaPervert(Crawler):
    base_url = "https://bakapervert.wordpress.com/"

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        assert possible_title, "No title found"
        self.novel_title = possible_title.text.rsplit("~", 1)[0].strip()
        logger.debug("Novel title = %s", self.novel_title)

        possible_cover = soup.select_one('meta[property="og:image"]')
        if possible_cover and "blank.jpg" not in possible_cover["content"]:
            self.novel_cover = possible_cover["content"]
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = "Downloaded from https://bakapervert.wordpress.com"
        logger.info("Novel author: %s", self.novel_author)

        # Removes none TOC links.
        toc_parts = soup.select_one(".entry-content")
        assert toc_parts, "No TOC found"
        for notoc in toc_parts.select(".sharedaddy, .code-block, script, .adsbygoogle"):
            notoc.extract()

        for a in soup.select('.entry-content a[href*="/bakapervert.wordpress.com/"]'):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
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
        contents = soup.select_one("div.entry-content")
        assert contents, "No contents found"

        for content in contents.select("p"):
            for bad in ["Prev", "Next"]:
                if bad in content.text:
                    content.extract()

        return self.cleaner.extract_contents(contents)
