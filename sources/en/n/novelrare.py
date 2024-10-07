# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class NovelrareCrawler(Crawler):
    base_url = "https://novelrare.com/"

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("#manga-title h1")
        if possible_title:
            self.novel_title = possible_title.get_text(strip=True)

        logger.info("Novel title: %s", self.novel_title)

        possible_synopsis = soup.select_one("div[aria-labelledby='manga-info'] p")
        if possible_synopsis:
            self.novel_synopsis = possible_synopsis.get_text()

        img_src = soup.select_one("div.summary_image img")
        if img_src:
            self.novel_cover = self.absolute_url(img_src["src"])

        chapters_table = soup.select_one("div.listing-chapters_wrap")
        for a in reversed(
            chapters_table.find_all("a", class_=lambda x: x != "c-new-tag")
        ):
            chap_id = 1 + (len(self.chapters))

            self.chapters.append(
                {
                    "id": chap_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a['href'])
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.select_one("div.text-left")
        return self.cleaner.extract_contents(content)
