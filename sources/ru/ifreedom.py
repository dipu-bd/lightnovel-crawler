# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class IfreedomCrawler(Crawler):
    base_url = [
        "https://ifreedom.su/",
        "https://bookhamster.ru/"
    ]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        if possible_title:
            self.novel_title = possible_title.get_text()

        logger.info("Novel title: %s", self.novel_title)

        possible_author = soup.select_one("span.dashicons-admin-users").next\
            .next\
            .next
        if "Не указан" not in str(possible_author):
            self.novel_author = possible_author.get_text()
            logger.info("Novel author: %s", self.novel_author)

        possible_full_synopsis = soup.select_one("span.open-desc")
        if possible_full_synopsis:
            possible_full_synopsis = possible_full_synopsis["onclick"]
            self.novel_synopsis = possible_full_synopsis.split("= '")[1].strip("';")
        else:
            self.novel_synopsis = soup.select_one("div.descr-ranobe").get_text()

        img_src = soup.select_one("div.img-ranobe img")
        if img_src:
            self.novel_cover = self.absolute_url(img_src["src"])

        for a in reversed(soup.select(".menu-ranobe a")):
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
        content = soup.select_one("div.entry-content")
        return self.cleaner.extract_contents(content)
