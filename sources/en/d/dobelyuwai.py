# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Dobelyuwai(Crawler):
    has_mtl = True
    base_url = "https://dobelyuwai.wordpress.com/"

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(["Prev", "ToC", "Next"])

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
        if "blank.jpg" in self.novel_cover:
            self.novel_cover = None
        logger.info("Novel cover: %s", self.novel_cover)

        # try:
        #     self.novel_author = soup.select_one('div.entry-content > p:nth-child(2)').text.strip()
        # except Exception as e:
        #     logger.warning('Failed to get novel auth. Error: %s', e)
        # logger.info('%s', self.novel_author)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one("div.entry-content")

        for notoc in toc_parts.select(
            ".sharedaddy, .inline-ad-slot, .code-block, script, .adsbygoogle"
        ):
            notoc.extract()

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.entry-content a[href*="https://dobelyuwai.wordpress.com/2"]'
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

        # Remoeves bad text from chapters.
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
