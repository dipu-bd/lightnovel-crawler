# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class RPGNovels(Crawler):
    base_url = ["https://rpgnovels.com/", "https://rpgnoob.wordpress.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            [
                "Previous Chapter",
                "Table of Contents",
                "Next Chapter",
                "Please consider supporting me. You can do this either by turning off adblock for this blog or via my . Thank you.",
            ]
        )

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_novel_cover = soup.select_one('meta[property="og:image"]')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["content"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.post-entry a[href*="mypage.syosetu.com"]')
            ]
        )
        logger.info("%s", self.novel_author)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one("div.post-entry")
        for notoc in toc_parts.select(".sharedaddy"):
            notoc.extract()

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select('div.post-entry li a[href*="rpg"]')

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

        body_parts = soup.select_one("div.post-entry")

        # Fixes images, so they can be downloaded.
        # all_imgs = soup.find_all('img')
        # for img in all_imgs:
        #     if img.has_attr('data-orig-file'):
        #         src_url = img['src']
        #         parent = img.parent
        #         img.extract()
        #         new_tag = soup.new_tag("img", src=src_url)
        #         parent.append(new_tag)

        return self.cleaner.extract_contents(body_parts)
