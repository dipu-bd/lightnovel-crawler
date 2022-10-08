# -*- coding: utf-8 -*-

import logging
import re

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

novel_url = "http://zenithnovels.com/%s/"


class ZenithNovelsCrawler(Crawler):
    base_url = "http://zenithnovels.com/"

    def read_novel_info(self):
        novel_id_search = re.search(r"(?<=zenithnovels.com/)[^/]+", self.novel_url)
        assert novel_id_search, "No novel id found"
        self.novel_id = novel_id_search.group(0)
        logger.info("Novel id: %s", self.novel_id)

        url = novel_url % self.novel_id
        soup = self.get_soup(url)

        possible_title = soup.select_one("article#the-post h1.name")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_cover = soup.select_one("article#the-post .entry img")
        if possible_cover:
            self.novel_cover = self.absolute_url(possible_cover["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        while True:
            self.parse_chapter_list(soup)

            next_link = soup.select_one("ul.lcp_paginator a.lcp_nextlink")
            if next_link:
                soup = self.get_soup(next_link["href"])
            else:
                break

        self.chapters.sort(key=lambda x: x["volume"] * 1e6 + x["id"])
        self.volumes = [{"id": x, "title": ""} for x in set(self.volumes)]

    def parse_chapter_list(self, soup):
        for a in soup.select("ul.lcp_catlist li a"):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
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

        entry = soup.select_one("article#the-post .entry")
        assert entry, "No chapter content entries"

        try:
            self.cleaner.clean_contents(entry)
            for note in entry.select(".footnote"):
                note.extract()
        except Exception:
            pass

        body = ""
        for tag in entry.children:
            if isinstance(tag, Tag) and tag.name == "p" and len(tag.text.strip()):
                p = " ".join(self.cleaner.extract_contents(tag))
                if len(p.strip()):
                    body += "<p>%s</p>" % p

        return body
