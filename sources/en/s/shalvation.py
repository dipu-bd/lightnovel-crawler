# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class ShalvationTranslations(Crawler):
    base_url = "https://shalvationtranslations.wordpress.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        # FIXME: Title has "Table of Content" text in title, same as website. I don't know how to remove it.
        self.novel_title = soup.find("h1", {"class": "entry-title"}).text.strip()
        logger.info("Novel title: %s", self.novel_title)

        # FIXME: Can't download cover image, saying "connot identify image" might because it's .png
        # self.novel_cover = self.absolute_url(
        #    soup.select_one('div.entry-content p img')['data-orig-file'])
        # logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select("div.entry-content p")[3].text.strip()
        logger.info("Novel author: %s", self.novel_author)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.entry-content p [href*="shalvationtranslations.wordpress.com/"]'
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

        body_parts = soup.select_one("div.entry-content")

        # Removes "Share this" text and buttons from bottom of chapters.
        for share in body_parts.select("div.sharedaddy"):
            share.extract()

        # Remoeves Nav Button from top and bottom of chapters.
        for content in body_parts.select("p"):
            for bad in ["PREVIOUS CHAPTER", "NEXT CHAPTER"]:
                if bad in content.text:
                    content.extract()

        # Remoeves span spacer.
        for content in body_parts.select("span"):
            for bad in ["Ο"]:
                if bad in content.text:
                    content.extract()

        return self.cleaner.extract_contents(body_parts)
