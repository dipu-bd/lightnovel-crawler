# -*- coding: utf-8 -*-
import logging

from bs4.element import Tag

import requests

from lncrawl.core.crawler import Crawler
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
search_url = "https://www.foxaholic.com/?s=%s&post_type=wp-manga"
# chapter_list_url = 'https://www.foxaholic.com/wp-admin/admin-ajax.php'


class FoxaholicCrawler(Crawler):
    base_url = [
        "https://foxaholic.com/",
        "https://www.foxaholic.com/",
        "https://18.foxaholic.com/",
        "https://global.foxaholic.com/",
    ]

    def initialize(self) -> None:
        self.init_executor(1)

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h3 a")
            if not isinstance(a, Tag):
                continue
            latest = tab.select_one(".latest-chap .chapter a")
            if isinstance(latest, Tag):
                latest = latest.text.strip()
            status = tab.select_one(".mg_release .summary-content a")
            if isinstance(status, Tag):
                status = "Status: " + status.text.strip()
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": " | ".join(filter(None, [latest, status])),
                }
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one(".summary_image a img")["data-src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="novel-author"]')
            ]
        )
        logger.info("%s", self.novel_author)

        if (
            "18.foxaholic.com" in self.novel_url
            or "global.foxaholic.com" in self.novel_url
        ):
            parsed_url = urlparse(self.novel_url)
            current_base_url = "%s://%s" % (parsed_url.scheme, parsed_url.hostname)

            novel_id = soup.select_one("#manga-chapters-holder")["data-id"]
            get_chapter_data = {"action": "manga_get_chapters", "manga": novel_id}

            response = self.submit_form(
                current_base_url + "/wp-admin/admin-ajax.php", data=get_chapter_data
            )

            soup = self.make_soup(response)

        for a in reversed(soup.select(".wp-manga-chapter a")):
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

        # REMINDER : Some chapters have additional protection in the form of having the actual
        # chapter url in the post. This selector might change frequently.

        blocked_chapter = soup.select_one(".text-left").find(
            lambda tag: tag.name == "a" and "Chapter" in tag.text
        )
        if blocked_chapter:
            logger.info("Blocked chapter detected. Trying to bypass...")
            soup = self.get_soup(blocked_chapter["href"])

        contents = soup.select_one(".entry-content_wrap")

        # all_imgs = soup.find_all('img')
        # for img in all_imgs:
        #     if img.has_attr('loading'):
        #         src_url = img['src']
        #         parent = img.parent
        #         img.extract()
        #         new_tag = soup.new_tag("img", src=src_url)
        #         parent.append(new_tag)
        return self.cleaner.extract_contents(contents)

    def download_image(self, url):
        logger.info("Foxaholic image: %s", url)
        response = requests.get(
            url,
            verify=False,
            allow_redirects=True,
            headers={
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.9"
            },
        )
        return response.content
