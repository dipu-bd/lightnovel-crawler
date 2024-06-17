# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

novel_toc_url = "https://genesistls.com/series/%s"
chapter_list_url = "http://gravitytales.com/novel/%s/chapters"


class GenesisTlsCrawler(Crawler):
    base_url = "https://genesistls.com"
    search_url = base_url + "/?s=%s"

    def search_novel(self, query):
        soup = self.get_soup(self.search_url % query)

        results = []
        for novel_article in soup.select(".listupd article"):
            novel_url = novel_article.select_one("a")["href"]
            novel_title = novel_article.select_one("span.ntitle").text
            novel_image = novel_article.select_one("img")["src"].split("?")[0]

            results.append(
                {
                    "url": novel_url,
                    "title": novel_title,
                    "img": novel_image
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        potential_novel_title = soup.select_one("h1.entry-title")
        assert potential_novel_title, "No novel title"
        self.novel_title = potential_novel_title.text
        logger.info("Novel title: %s", self.novel_title)

        potential_author = soup.select_one("a[href^=\"https://genesistls.com/writer/\"]")
        assert potential_author, "No author"
        self.novel_author = potential_author.text
        logger.info("Novel author: %s", self.novel_author)

        potential_cover = self.absolute_url(
            soup.select_one(".bigcontent img[itemprop=image]")["src"]
        ).split("?")[0]
        assert potential_cover, "No cover"
        self.novel_cover = potential_cover
        logger.info("Novel cover: %s", self.novel_cover)

        for ep_list_item in soup.select("article.hentry .eplister ul li"):

            # Check whether the chapter is paid and skip if true
            paid_chapter = ep_list_item.select_one("div.epl-price").text != "Free"
            if paid_chapter:
                continue

            chapter_id = len(self.chapters) + 1
            vol_id = chapter_id // 100 + 1

            potential_chapter_title = ep_list_item.select_one("div.epl-title").text
            chapter_title = potential_chapter_title if len(potential_chapter_title) else f"Chapter {len(self.chapters) + 1}"

            chapter_url = ep_list_item.select_one("a")["href"]

            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chapter_id,
                    "volume": vol_id,
                    "title": chapter_title,
                    "url": self.absolute_url(chapter_url)
                }
            )

        logger.debug(
            "%d chapters and %d volumes found", len(self.chapters), len(self.volumes)
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.epcontent")
        contents = self.cleaner.extract_contents(contents)
        return str(contents)
