# -*- coding: utf-8 -*-

import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class DSRealmTranslationsCrawler(Crawler):
    base_url = "https://dsrealmtranslations.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".page-title h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        self.novel_title = self.novel_title.split(":")[0].strip()
        logger.info("Novel title: %s", self.novel_title)

        # NOTE: Site list no cover images.
        # self.novel_cover = self.absolute_url(
        #     soup.select_one('div.entry-content p img')
        # logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "by DSRealmTranslations"
        logger.info("Novel author: %s", self.novel_author)

        # Extract volume-wise chapter entries
        # FIXME: Sometimes grabs social media link at bottom of page, No idea how to exclude links.
        # FIXME: Chapter title are url links, it's the way translator formatted website.
        chapters = soup.select('.wpb_wrapper p a[href*="dsrealmtranslations.com"]')

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
        contents = soup.select("div.wpb_wrapper")
        self.cleaner.clean_contents(contents)

        return str(contents)
