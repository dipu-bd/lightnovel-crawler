# -*- coding: utf-8 -*-
import logging
from bs4 import BeautifulSoup, Tag
import re
import njsparser

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException

logger = logging.getLogger(__name__)
logging.getLogger("njsparser").setLevel(logging.ERROR)

CHAPTER_LIST_URL = (
    "https://api.reaperscans.com/chapters/{}?page={}&perPage=100&order=asc"
)


class Reaperscans(Crawler):
    base_url = "https://reaperscans.com/"

    def initialize(self):
        self.cleaner.bad_text_regex = set(
            [
                "Translator",
                "Proofreader",
                "Reaper Scans",
                "REAPER SCANS",
                "https://dsc.gg/reapercomics",
                "https://discord.gg/MaRegMFhRb",
                "https://discord.gg/reapercomics",
                "h ttps://discord.gg/reapercomic",
                "https://discord.gg/sb2jqkv",
                "____",
                "Join our Discord",
            ]
        )
        self.init_executor(ratelimit=0.9)

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one("h1").text.strip()
        logger.info("Novel title: %s", self.novel_title)

        match = re.search(r'\\"series_id\\":(\d+)', soup.prettify())
        if match:
            self.novel_id = int(match.group(1))
        else:
            raise LNException("Could not find series_id in the page source")

        logger.info("Novel ID %d", self.novel_id)

        possible_image = soup.select_one(".h-full .w-full img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        chapters = []
        data = self.get_json(CHAPTER_LIST_URL.format(self.novel_id, 1))
        chapters += data["data"]

        futures = []
        for page in range(2, data["meta"]["last_page"] + 1):
            url = CHAPTER_LIST_URL.format(self.novel_id, page)
            futures.append(self.executor.submit(self.get_json, url))

        for f in futures:
            data = f.result()
            chapters += data["data"]

        for item in chapters:
            chap_id = 1 + (len(self.chapters))
            chap_name = item["chapter_name"]
            self.chapters.append(
                {
                    "id": chap_id,
                    "url": f"{self.novel_url}/{item['chapter_slug']}",
                    "title": chap_name if chap_name else item["chapter_title"],
                }
            )

    def download_chapter_body(self, chapter):
        response = self.get_response(chapter["url"], timeout=10)
        html_text = response.content.decode("utf8", "ignore")
        fd = njsparser.BeautifulFD(html_text)

        for data in fd.find_iter([njsparser.Text]):
            if data.value is not None:
                break
            else:
                raise LNException("Could not get chapter content for %s", chapter["url"])

        content = BeautifulSoup(data.value, "lxml")
        return self.cleaner.extract_contents(content)
