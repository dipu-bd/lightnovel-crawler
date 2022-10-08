# -*- coding: utf-8 -*-
import logging
from bs4 import Tag
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://fanstranslations.com/?post_type=wp-manga&s=%s"
wp_admin_ajax_url = "https://fanstranslations.com/wp-admin/admin-ajax.php"


def initialize(self) -> None:
    self.cleaner.blacklist_patterns.update(
        [
            r"^Translator Thoughts:",
            r"^Please leave some comments to show your support~",
            r"^Please some some positive reviews on NovelUpate",
            r"^AI CONTENT END 2",
            r"^Please leave some some positive reviews on Novel Updates",
            r"^Check how can you can have me release Bonus Chapters",
            r"^Please subscribe to the blog ~",
            r"^Please click on the ad in the sidebar to show your support~",
            r"^Access to advance chapters and support me",
            r"^Access to 2 advance chapters and support me",
            r"^Check out other novels on Fan’s Translation ~",
            r"^Support on Ko-fi",
            r"^Get  on Patreon",
            r"^Check out other novels on Fan’s Translation~",
            r"^to get Notification for latest Chapter Releases",
        ]
    )
    self.cleaner.bad_tags.update(["a"])


class FansTranslations(Crawler):
    base_url = "https://fanstranslations.com/"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

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
        logger.debug("Visiting %s", self.novel_url)
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
                for a in soup.select('.author-content a[href*="novel-author"]')
            ]
        )
        logger.info("%s", self.novel_author)

        possible_novel_id = soup.select_one("#manga-chapters-holder")
        assert isinstance(possible_novel_id, Tag), "No novel id"
        self.novel_id = possible_novel_id["data-id"]
        logger.info("Novel id: %s", self.novel_id)

        response = self.submit_form(self.novel_url.strip("/") + "/ajax/chapters")
        soup = self.make_soup(response)
        for a in reversed(soup.select("li.wp-manga-chapter a")):
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
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div.text-left")
        assert isinstance(contents, Tag), "No contents"
        return self.cleaner.extract_contents(contents)
