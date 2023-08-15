# -*- coding: utf-8 -*-
import logging
import json
import operator

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class RanobeLibMeCrawler(Crawler):
    base_url = [
        "https://ranobelib.me/",
    ]

    def initialize(self):
        self.init_executor(1)

    def read_novel_info(self):
        clean_url = self.novel_url.split("?")[0].strip("/")
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(f"{clean_url}?section=info")

        for script in soup.find_all("script"):
            json_var = "window.__DATA__ = "
            text = script.text.strip()
            if not text or not text.startswith(json_var):
                continue
            text = text[len(json_var) : text.find("window._SITE_COLOR_")].strip(
                ";\t\n "
            )
            content = json.loads(text)

        self.novel_title = content["manga"]["rusName"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one(".media-sidebar__cover > img:nth-child(1)")["src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = soup.select_one(
            "div.media-info-list__item:nth-child(6) > div:nth-child(2) > a:nth-child(1)"
        ).text.strip()
        logger.info("Novel author: %s", self.novel_author)

        self.novel_synopsis = self.cleaner.extract_contents(
            soup.find("div", {"class": "media-description__text"})
        )
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        for tag in soup.find_all("a", {"class": "media-tag-item"}):
            self.novel_tags.append(tag.text)
        logger.info("Novel tags: %s", self.novel_tags)

        chapters = content["chapters"]["list"]
        chapters.reverse()
        chap_id = 0
        volumes_set = set()

        branches = dict()
        for chapter in chapters:
            key = chapter["branch_id"]
            branches[key] = branches.setdefault(key, 0) + 1
        branch = max(branches.items(), key=operator.itemgetter(1))[0]

        for chapter in chapters:
            if chapter["branch_id"] != branch:
                continue

            chap_id = chap_id + 1
            chap_num = chapter["chapter_number"]
            vol_id = chapter["chapter_volume"]

            if vol_id not in volumes_set:
                volumes_set.add(vol_id)
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(
                        f"{clean_url}/v{str(vol_id)}/c{chap_num}/"
                    ),
                    "title": chapter["chapter_name"] or (f"Глава {chap_num}"),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".reader-container")
        self.cleaner.clean_contents(contents)
        return str(contents)
