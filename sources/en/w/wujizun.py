# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Chapter, LegacyCrawler, Volume

logger = logging.getLogger(__name__)


class Wujizun(LegacyCrawler):
    base_url = "https://wujizun.com/"

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            ["Previous Chapter", "Table of Contents", "Next Chapter", "MYSD Patreon:"]
        )

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one('meta[property="og:image"]')
        if possible_image:
            self.novel_cover = possible_image["content"]
        logger.info("Novel cover: %s", self.novel_cover)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one("div.entry-content")
        for notoc in toc_parts.select(
            ".sharedaddy, .ezoic-adpicker-ad, .ezoic-ad-adaptive, .ezoic-ad"
        ):
            notoc.extract()

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        for a in soup.select('div.entry-content p a[href*="wujizun.com/2"]'):
            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append(Volume(id=vol_id))
            self.chapters.append(
                Chapter(
                    id=chap_id,
                    volume=vol_id,
                    url=self.absolute_url(a["href"]),
                    title=a.text.strip() or "Chapter %d" % chap_id,
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        body_parts = soup.select_one("div.entry-content")
        self.cleaner.clean_contents(body_parts)
        return str(body_parts)
