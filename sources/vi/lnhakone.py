# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import quote_plus

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "%s/tim-kiem-nang-cao?title=%s"
chapter_list_url = "https://listnovel.com/wp-admin/admin-ajax.php"


class ListNovelCrawler(Crawler):
    has_mtl = True
    base_url = [
        "https://ln.hako.vn/",
        "https://docln.net/",
    ]

    def initialize(self):
        self.init_executor(1)

    def search_novel(self, query):
        query = quote_plus(query.lower())
        soup = self.get_soup(search_url % (self.home_url.strip("/"), query))

        results = []
        for tab in soup.select(".sect-body .thumb-item-flow"):
            a = tab.select_one(".series-title a")
            latest_vol = tab.select_one(".volume-title").text.strip()
            latest_chap = tab.select_one(".chapter-title a")["title"]
            results.append(
                {
                    "title": a["title"],
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | %s" % (latest_vol, latest_chap),
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".series-name a")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = " ".join(
            [a.text.strip() for a in soup.select('.info-value a[href*="/tac-gia/"]')]
        )
        logger.info("%s", self.novel_author)

        possible_image = soup.select_one(".series-cover .img-in-ratio")
        if isinstance(possible_image, Tag):
            urls = re.findall(r"url\('([^']+)'\)", str(possible_image["style"]))
            self.novel_cover = self.absolute_url(urls[0]) if urls else None
        logger.info("Novel cover: %s", self.novel_cover)

        for section in soup.select(".volume-list"):
            vol_id = 1 + len(self.volumes)
            vol_title = section.select_one(".sect-title")
            vol_title = vol_title.text.strip() if isinstance(vol_title, Tag) else None
            self.volumes.append(
                {
                    "id": vol_id,
                    "title": vol_title,
                }
            )
            for a in section.select(".list-chapters a"):
                chap_id = 1 + len(self.chapters)
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": vol_id,
                        "title": a["title"],
                        "url": self.absolute_url(a["href"]),
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select("#chapter-content p")
        return "".join([str(p) for p in contents])
