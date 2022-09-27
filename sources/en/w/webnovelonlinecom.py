# -*- coding: utf-8 -*-
import re
import json
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class WebnovelOnlineDotComCrawler(Crawler):
    base_url = "https://webnovelonline.com/"

    def read_novel_info(self):
        url = self.novel_url
        soup = self.get_soup(url)

        possible_title = soup.select_one(".novel-info .novel-desc h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_novel_cover = soup.select_one('meta[property="og:image"]')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["content"])
        logger.info("Novel cover: %s", self.novel_title)

        volumes = set([])
        for a in reversed(soup.select(".chapter-list .item a")):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

        self.volumes = [{"id": x, "title": ""} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        for script in soup.select("script"):
            text = script.string
            if not text or not text.startswith("window._INITIAL_DATA_"):
                continue
            content = re.findall(r',"chapter":(".+")},', text)[0]
            content = json.loads(content).strip()
            return "<p>" + "</p><p>".join(content.split("\n\n")) + "</p>"

        return ""
