# -*- coding: utf-8 -*-

import logging
import requests
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Chireads(Crawler):
    base_url = ["https://chireads.com/"]
    has_manga = False
    has_mtl = False

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")

        # NOTE: Using self.get_soup() here throw an error, I don't know why.
        response = requests.get("https://chireads.com/search?x=0&y=0&name=" + query)
        soup = self.make_soup(response)

        result = []
        content = soup.find("div", {"id": "content"})

        for novel in content.find_all("li"):
            content = novel.find("a")
            result.append(
                {
                    "title": content.get("title"),
                    "url": self.absolute_url(content.get("href")),
                }
            )

        return result

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        content = soup.find("div", {"class": "conteiner"}).find_all(
            "div", {"class": "wid"}
        )

        metadata = content[0]
        self.novel_cover = self.absolute_url(metadata.find("img").get("src"))

        self.novel_title = (
            metadata.find("h3", {"class": "inform-title"}).text.split("|")[0].strip()
        )

        self.novel_author = (
            metadata.find("h6", {"class": "font-color-black3"})
            .text.split("\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0")[0]
            .replace("Auteur : ", "")
        )

        body = content[1]
        tomes = body.find_all("div", {"class": "chapitre"})
        for vol_id, tome in enumerate(tomes, 1):
            self.volumes.append(
                {
                    "id": vol_id,
                    "title": tome.find("div", {"class": "title"}).text,
                }
            )
            for chapter in tome.find_all("a"):
                chap_id = len(self.chapters) + 1
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": vol_id,
                        "url": self.absolute_url(chapter.get("href")),
                        "title": chapter.text.replace("\xa0", " "),
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.find(
            "div",
            {
                "id": "content",
                "class": "font-color-black3 article-font",
            },
        )
        return self.cleaner.extract_contents(content)
