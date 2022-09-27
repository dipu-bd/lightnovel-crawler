# -*- coding: utf-8 -*-
import logging
import re
import ast
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

book_url = "https://mangatoon.mobi/%s/detail/%s/episodes"
search_url = "https://mangatoon.mobi/%s/search?word=%s"


class MangatoonMobiCrawler(Crawler):
    base_url = [
        "https://mangatoon.mobi/",
    ]

    def initialize(self):
        self.home_url = "https://mangatoon.mobi"

    def read_novel_info(self):
        novel_id = self.novel_url.split("/")[5]
        logger.info("Novel Id: %s", novel_id)

        novel_region = self.novel_url.split("/")[3]
        logger.info("Novel Region: %s", novel_region)

        self.novel_url = book_url % (novel_region, novel_id)
        logger.debug("Visiting %s", self.novel_url)

        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.comics-title, .detail-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".detail-top-right img, .detail-img .big-img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        volumes = set([])
        for a in soup.select("a.episode-item, a.episode-item-new"):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.select_one(".episode-title, .episode-title-new").text,
                }
            )

        self.volumes = [{"id": x} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        pictures = soup.select_one(".pictures")
        if pictures:
            return str(pictures)

        script = soup.find("script", text=re.compile(r"initialValue\s+="))
        initialValue = re.search("var initialValue = (?P<value>.*);", script.string)
        content = initialValue.group("value")

        chapter_content = ast.literal_eval(content)
        chapter_content = [p.replace(r"\-", "-") for p in chapter_content]
        chapter_content = [p.replace("\\", "") for p in chapter_content]
        return "<p>" + "</p><p>".join(chapter_content) + "</p>"
