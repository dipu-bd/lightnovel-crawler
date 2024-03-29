# -*- coding: utf-8 -*-
import json
import logging

from colorama import Fore, Style
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

chapters_api = "https://api.renovels.org/api/titles/chapters/?branch_id={}\
                &ordering=-index&user_data=1&count=100&page={}"


class RenovelsCrawler(Crawler):
    base_url = ["https://renovels.org/"]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        script = json.loads(soup.select_one("script#__NEXT_DATA__").get_text())
        novel_id = script["props"]["pageProps"]["fallbackData"]["content"]['branches'][0]["id"]

        possible_title = soup.select_one("h1[itemprop='name']")
        if possible_title:
            self.novel_title = possible_title.get_text().split("[")[0]

        logger.info("Novel title: %s", self.novel_title)

        possible_synopsis = soup.select_one("div[itemprop='description']")
        if possible_synopsis:
            self.novel_synopsis = possible_synopsis.get_text()
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        img_src = script["props"]["pageProps"]["fallbackData"]["content"]['img']['high']
        self.novel_cover = self.base_url[0].rstrip("/") + img_src
        logger.info("Novel cover: %s", self.novel_cover)

        page = 1
        pre_chapters = []
        while True:
            chapters = self.get_json(chapters_api.format(novel_id, page))["content"]
            for chapter in chapters:
                pre_chapters.append(chapter)

            if chapters[-1]["index"] == 1:
                break
            page += 1

        if self.novel_url.endswith("about") or self.novel_url.endswith("content"):
            self.novel_url = self.novel_url.split("?")[0]

        for chapter in reversed(pre_chapters):
            chap_id = 1 + (len(self.chapters))
            chap_name = chapter["name"]
            self.chapters.append(
                {
                    "id": chap_id,
                    "title": chap_name if chap_name else chapter["chapter"],
                    "url": f"{self.novel_url}/{chapter['id']}"
                }
            )

        print(
            "\n",
            Style.BRIGHT,
            Fore.RED,
            "!!! NOTICE:",
            Fore.RESET,
            "The site blocks the connection after 1400 chapters. "
            "It is recommended not to download more than 1300 chapters at one time.",
            Style.RESET_ALL,
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.select_one("script#__NEXT_DATA__").get_text()
        content = self.make_soup(
            json.loads(content)["props"]["pageProps"]["fallbackData"]["chapter"]["content"]["content"]
        )
        return self.cleaner.extract_contents(content)
