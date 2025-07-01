# -*- coding: utf-8 -*-
import logging
import re

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class RequieMtlsCrawler(Crawler):
    base_url = ["https://requiemtls.com/"]
    has_mtl = True

    def initialize(self):
        self.init_executor(ratelimit=0.99)

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(".infox .entry-title").text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".thumbook .thumb img")
        if isinstance(possible_image, Tag):
            self.novel_cover = possible_image["src"]
        logger.info("Novel cover: %s", self.novel_cover)

        possible_synopsis = soup.select(".entry-content p")
        if possible_synopsis:
            self.novel_synopsis = "".join([str(p) for p in possible_synopsis])
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        for a in reversed(soup.select(".eplisterfull ul li a")):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.select_one(".epl-title").text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    font_ranges = {
        "requiem_tnr_g1": (0x10A0, 0x10FD, 47),
        "requiem_fs_g1": (0x10A0, 0x10FD, 47),
        "requiem_tnr_k1": (0x30A0, 0x30FD, 47),
        "requiem_fs_k1": (0x30A0, 0x30FD, 47),
        "requiem_tnr_s1": (0x1B80, 0x1BDD, 47),
        "requiem_fs_s1": (0x1B80, 0x1BDD, 47),
    }

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        div = soup.select_one(".epcontent.entry-content")
        font = div["style"].split(";")
        for f in font:
            if "font-family" in f:
                font = f
                break

        font = re.sub("[\\s'\"]", "", font)
        font = font.replace("font-family:", "").split(",")
        for f in font:
            if "requiem" in f:
                font = f
                break
        logger.info(font)

        contents = soup.select(".epcontent.entry-content p")
        body = "".join([str(self.cleaner.clean_contents(p)) for p in contents])

        minc, maxc, rot = self.font_ranges[font]
        newbody = ""
        for i in range(len(body)):
            c = ord(body[i])
            if c >= minc and c <= maxc:
                newbody += chr((c - minc + rot) % (maxc - minc + 1) + ord("!"))
            else:
                newbody += body[i]
        return newbody
