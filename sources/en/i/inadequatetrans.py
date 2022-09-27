# -*- coding: utf-8 -*-

import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class InadequateTranslations(Crawler):
    base_url = "https://inadequatetranslations.wordpress.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("a", {"aria-current": "page"}).text.strip()
        logger.info("Novel title: %s", self.novel_title)

        # TODO: Site list no cover images.
        # self.novel_cover = self.absolute_url(
        #     soup.select_one('div.entry-content p img')
        # logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "by Inadequate Translations"
        logger.info("Novel author: %s", self.novel_author)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one(".entry-content")
        for notoc in toc_parts.select(".sharedaddy"):
            notoc.extract()

        # Extract volume-wise chapter entries
        chapters = soup.select(
            '.entry-content a[href*="inadequatetranslations.wordpress.com"]'
        )

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

        body = []
        contents = soup.select("div.entry-content p")
        for p in contents:
            para = self.cleaner.extract_contents(p)
            if para:
                body.append(para)

        return "<p>%s</p>" % "</p><p>".join(body)
