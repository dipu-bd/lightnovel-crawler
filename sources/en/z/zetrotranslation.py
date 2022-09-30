# -*- coding: utf-8 -*-

import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
ajax_url = "%s/wp-admin/admin-ajax.php"


class ZetroTranslationCrawler(Crawler):
    base_url = ["https://zetrotranslation.com/"]

    search_url = "%s?s=%s&post_type=wp-manga&author=&artist=&release="

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3", "script"])
        self.cleaner.bad_css.update([".code-block", ".adsbygoogle"])

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(self.search_url % (self.home_url, query))

        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h3 a")
            latest = tab.select_one(".latest-chap .chapter a").text
            votes = tab.select_one(".rating .total_votes").text
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | Rating: %s" % (latest, votes),
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title h1")
        for span in possible_title.select("span"):
            span.extract()

        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        img_src = soup.select_one(".summary_image a img")

        if img_src:
            self.novel_cover = self.absolute_url(img_src["src"])

        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="manga-author"]')
            ]
        )
        logger.info("Novel author: %s", self.novel_author)

        self.novel_id = soup.select_one("#manga-chapters-holder")["data-id"]

        response = self.submit_form(
            ajax_url % self.home_url.rstrip("/"),
            data={
                "action": "manga_get_chapters",
                "manga": self.novel_id,
            },
        )

        soup = self.make_soup(response)
        chap_list = soup.select(".wp-manga-chapter:not(.premium-block) a")
        for a in reversed(chap_list):
            chap_id = len(self.chapters) + 1
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
        contents = soup.select_one("div.reading-content")

        return self.cleaner.extract_contents(contents)
