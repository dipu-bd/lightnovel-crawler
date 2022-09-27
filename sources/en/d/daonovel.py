# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://daonovel.com/?s=%s&post_type=wp-manga&author=&artist=&release="


class DaoNovelCrawler(Crawler):
    base_url = "https://daonovel.com/"

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".c-tabs-item__content")[:20]:
            a = tab.select_one(".post-title h3 a")
            if not isinstance(a, Tag):
                continue

            info = []
            latest = tab.select_one(".latest-chap .chapter a")
            if isinstance(latest, Tag):
                info.append(latest.text.strip())

            votes = tab.select_one(".rating .total_votes")
            if isinstance(votes, Tag):
                info.append("Rating: " + votes.text.strip())

            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": " | ".join(info),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title h1")
        assert isinstance(possible_title, Tag)
        for span in possible_title.select("span"):
            span.extract()
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".summary_image a img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="manga-author"]')
            ]
        )
        logger.info("%s", self.novel_author)

        chapter_list_url = self.absolute_url("ajax/chapters", self.novel_url)
        soup = self.post_soup(chapter_list_url, headers={"accept": "*/*"})
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
        contents = soup.select(".reading-content p")
        return "".join([str(p) for p in contents])
