# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler
from bs4 import Comment

logger = logging.getLogger(__name__)
search_url = "https://morenovel.net/?s=%s&post_type=wp-manga&author=&artist=&release="


class ListNovelCrawler(Crawler):
    base_url = "https://morenovel.net/"

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
        """Get novel title, autor, cover etc"""
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title h1")
        for span in possible_title.select("span"):
            span.extract()

        self.novel_title = possible_title.text.strip()
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

        self.novel_id = soup.select_one("#manga-chapters-holder")["data-id"]
        logger.info("Novel id: %s", self.novel_id)

        response = self.submit_form(self.novel_url.strip('/') + '/ajax/chapters')
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
        """Download body of a single chapter and return as clean html format."""
        logger.info("Visiting %s", chapter["url"])
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.text-left")

        for bad in contents.select(
            ".code-block, script, .adsbygoogle, .adsense-code, .sharedaddy, a, br"
        ):
            bad.extract()

        # Remove html comments from bottom of chapters.
        for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        return self.cleaner.extract_contents(contents)
