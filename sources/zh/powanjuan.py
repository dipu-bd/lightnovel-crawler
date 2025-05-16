# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class PowanjuanCrawler(Crawler):
    base_url = "https://www.powanjuan.cc/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url, encoding='gb2312')

        possible_title = soup.select_one(".desc h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.split('(')[0].strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_novel_author = soup.select_one('.descTip span')
        if possible_novel_author:
            self.novel_author = possible_novel_author.text.replace('作者：', '').strip()
        logger.info("Novel author: %s", self.novel_author)

        possible_synopsis = soup.select_one('.descInfo p')
        if possible_synopsis:
            self.novel_synopsis = possible_synopsis.text
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        volumes = set([])
        for a in soup.select(".catalog ul.clearfix li a"):
            ch_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": ch_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

        self.volumes = [{"id": x, "title": ""} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"], encoding='gb2312')
        contents = soup.select_one("#mycontent")
        return self.cleaner.extract_contents(contents)
