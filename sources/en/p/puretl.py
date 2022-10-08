# -*- coding: utf-8 -*-

import logging
import re

from bs4 import Tag
from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException

logger = logging.getLogger(__name__)


class PureTL(Crawler):
    base_url = ["https://puretl.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            [
                "Consider supporting Pure and whitelisting",
                "If you enjoy this novel, please consider turning off ad-block! thank you~",
                "Check out our weekly update schedule HERE",
            ],
        )

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        slug = re.search(rf"{self.home_url}(.*?)(/|\?|$)", self.novel_url).group(1)

        title_tag = soup.select_one("meta[property='og:title']")
        if not isinstance(title_tag, Tag):
            raise LNException("No title found")

        self.novel_title = (
            title_tag["content"]
            .replace("— Pure Love Translations English Translated Novels", "")
            .strip()
        )

        possible_image = soup.select_one("meta[property='og:image']")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["content"])

        logger.info("Novel cover: %s", self.novel_cover)

        novel_author = soup.find("h4", string=re.compile(r"^By:"))
        if isinstance(novel_author, Tag):
            self.novel_author = novel_author.text.split(":")[1].strip()

        logger.info("Novel author: %s", self.novel_author)

        chapter_div = soup.find("div", class_="accordion-block")
        if not isinstance(chapter_div, Tag):
            raise LNException("No chapters found")

        content = chapter_div.find_parent("section")

        for a in content.select(f"a[href*='{slug}/']"):
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip(),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        chapter["title"] = soup.select_one(".entry-title").text.strip()

        contents = soup.select_one(".blog-item-content")
        nav = contents.find("a", string=re.compile("Index"))
        if isinstance(nav, Tag):
            nav.parent.extract()

        return self.cleaner.extract_contents(contents)
