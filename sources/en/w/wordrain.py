# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://wordrain69.com/?s=%s"
post_chapter_suffix = "/ajax/chapters/"


class WordRain(Crawler):
    base_url = "https://wordrain69.com"

    def initialize(self):
        self.cleaner.bad_tags.update(
            [
                "a",
                "h3",
                "script",
            ]
        )
        self.cleaner.bad_css.update(
            [
                ".code-block",
                ".adsbygoogle",
                ".adsense-code",
                ".sharedaddy",
            ]
        )

    # NOTE: Site search doesn't work. So this won't work.
    """
    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.c-tabs-item__content'):
            a = tab.select_one('.post-title h3 a')
            latest = tab.select_one('.latest-chap .chapter a').text
            votes = tab.select_one('.rating .total_votes').text
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '%s | Rating: %s' % (latest, votes),
            })

        return results
    """

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert isinstance(possible_title, Tag), "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one('meta[property="og:image"]')
        if isinstance(possible_image, Tag):
            self.novel_cover = possible_image["content"]
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="manga-translator"]')
            ]
        )
        logger.info("%s", self.novel_author)

        self.novel_id = self.novel_url.removesuffix("/").split("/")[-1]
        logger.info("Novel id: %s", self.novel_id)

        post_chapter_url = f"{self.base_url[0]}/manga/{self.novel_id}{post_chapter_suffix}"

        logger.info("Sending post request to %s", post_chapter_url)
        response = self.submit_form(
            post_chapter_url,
        )
        soup = self.make_soup(response)
        for a in reversed(soup.select(".wp-manga-chapter > a")):
            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            if len(self.chapters) % 100 == 0:
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
        return self.cleaner.extract_contents(contents)
