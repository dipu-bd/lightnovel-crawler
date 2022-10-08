# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class ShinsoriCrawler(Crawler):
    base_url = "https://www.shinsori.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("span.the-section-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = None
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = (
            "Author : %s, Translator: Shinsori"
            % soup.select("div.entry.clearfix p strong")[1].next_sibling.strip()
        )
        logger.info("Novel author: %s", self.novel_author)

        # get pagination range
        p_range = int(soup.select("ul.lcp_paginator li")[-2].text)

        chapters = []
        # get chapter list by looping pagination range
        for x in range(p_range):
            p_url = "%s?lcp_page0=%d#lcp_instance_0 x+1" % (self.novel_url, x + 1)
            p_soup = self.get_soup(p_url)
            chapters.extend(p_soup.select("ul.lcp_catlist")[1].select("li a"))

        for x in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(x["href"]),
                    "title": x["title"] or ("Chapter %d" % chap_id),
                }
            )

        self.volumes = [{"id": x + 1} for x in range(len(self.chapters) // 100 + 1)]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        content = soup.select_one("div.entry-content")

        # remove div with no class
        for item in content.findAll("div", attrs={"class": None}):
            item.extract()

        # remove style
        for item in content.findAll("style"):
            item.extract()

        subs = "tab"
        # remove all div that has class but not relevant
        for item in content.findAll("div"):
            res = [x for x in item["class"] if re.search(subs, x)]
            if len(res) == 0:
                item.extract()

        # remove p with attribute style
        for item in content.findAll("p"):
            if item.has_attr("style"):
                item.extract()

        return str(content)
