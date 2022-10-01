# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "%s/?s=%s&post_type=wp-manga&author=&artist=&release="


class BoxNovelCrawler(Crawler):
    base_url = [
        "https://boxnovel.com/",
    ]

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % (self.home_url, query))

        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h4 a")
            if not isinstance(a, Tag):
                continue
            latest = tab.select_one(".latest-chap .chapter a")
            latest = latest.text if isinstance(latest, Tag) else ""
            votes = tab.select_one(".rating .total_votes")
            votes = votes.text if isinstance(votes, Tag) else ""
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

        possible_title = soup.select_one('meta[property="og:title"]')
        assert isinstance(possible_title, Tag), "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one('meta[property="og:image"]')
        if isinstance(possible_image, Tag):
            self.novel_cover = possible_image["content"]
        logger.info("Novel cover: %s", self.novel_cover)

        try:
            author = soup.select(".author-content a")
            if len(author) == 2:
                self.novel_author = author[0].text + " (" + author[1].text + ")"
            else:
                self.novel_author = author[0].text
        except Exception as e:
            logger.debug("Failed to parse novel author. %s", e)
        logger.info("Novel author: %s", self.novel_author)

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
