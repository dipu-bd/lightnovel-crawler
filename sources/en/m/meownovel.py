# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = (
    "https://meownovel.com/?s=%s&post_type=wp-manga&op=&author=&artist=&release=&adult="
)


class MeowNovel(Crawler):
    base_url = "https://meownovel.com/"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                "a",
                ".google-auto-placed",
                ".ap_container",
            ]
        )
        self.cleaner.bad_text_regex.update(
            [
                "Read First at meownovel.com",
                "Latest Update on meow novel.com",
                "me ow no vel.com is releasing your favorite novel",
                "You can read this novel at m eow no vel.com for better experience",
                "meow novel . com will be your favorite novel site",
                "Read only at m e o w n o v e l . c o m",
            ]
        )

    def search_novel(self, query):
        soup = self.get_soup(search_url % quote(query.lower()))

        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h3 a")
            latest = tab.select_one(".latest-chap .chapter a").text
            votes = tab.select_one(".rating .total_votes").text
            results.append(
                {
                    "title": a.text.rsplit(" | ", 1)[0].strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | Rating: %s" % (latest, votes),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert isinstance(possible_title, Tag), "No novel title"
        self.novel_title = possible_title["content"]
        self.novel_title = self.novel_title.rsplit(" | ", 1)[0].strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one('meta[property="og:image"]')
        if isinstance(possible_image, Tag):
            self.novel_cover = possible_image["content"]
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="novel-author"]')
            ]
        )
        logger.info("%s", self.novel_author)

        self.novel_id = soup.select_one("#manga-chapters-holder")["data-id"]
        logger.info("Novel id: %s", self.novel_id)

        response = self.submit_form(self.novel_url.strip("/") + "/ajax/chapters")
        soup = self.make_soup(response)
        for a in reversed(soup.select(".wp-manga-chapter a")):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        logger.info("Visiting %s", chapter["url"])
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div.text-left")
        return self.cleaner.extract_contents(contents)
