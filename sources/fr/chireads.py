# -*- coding: utf-8 -*-

import logging
from lncrawl.core.crawler import Crawler
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Chireads(Crawler):
    base_url = ["https://chireads.com/"]
    has_manga = False
    machine_translation = False

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")

        # Using self.get_soup() here throw an error, I don't know why.
        response = requests.get("https://chireads.com/search?x=0&y=0&name=" + query)
        soup = BeautifulSoup(response.text, "html.parser")

        result = []
        content = soup.find("div", {"id": "content"})

        for novel in content.find_all("li"):
            content = novel.find("a")
            result.append({"title": content.get("title"), "url": content.get("href")})

        return result

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        content = soup.find("div", {"class": "conteiner"}).find_all(
            "div", {"class": "wid"}
        )

        metadata = content[0]
        self.novel_cover = metadata.find("img").get("src").strip()
        self.novel_title = self.cleaner.clean_text(
            metadata.find("h3", {"class": "inform-title"}).text.split("|")[0]
        )
        self.novel_author = self.cleaner.clean_text(
            metadata.find("h6", {"class": "font-color-black3"})
            .text.split("\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0")[0]
            .replace("Auteur : ", "")
        )

        body = content[1]

        self.chapters = []
        self.volumes = []

        tomes = body.find_all("div", {"class": "chapitre"})

        chap_nmbr = 1
        for i, tome in enumerate(tomes, 1):
            self.volumes.append(
                {
                    "id": i,
                    "title": self.cleaner.clean_text(
                        tome.find("div", {"class": "title"}).text
                    ),
                }
            )

            for chapter in tome.find_all("a"):
                self.chapters.append(
                    {
                        "id": chap_nmbr,
                        "volume": i,
                        "url": chapter.get("href").strip(),
                        "title": self.cleaner.clean_text(
                            chapter.text.replace("\xa0", " ")
                        ),
                    }
                )
                chap_nmbr += 1

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        return self.cleaner.extract_contents(
            soup.find(
                "div", {"id": "content", "class": "font-color-black3 article-font"}
            )
        )
