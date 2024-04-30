# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ChrysanthemumGarden(Crawler):
    base_url = "https://chrysanthemumgarden.com/"

    def read_novel_info(self):
        if not self.novel_url.endswith("/"):
            self.novel_url += "/"
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.novel-title")
        assert possible_title, "No novel title"
        raw_title = possible_title.select_one("span")
        if raw_title:
            raw_title.extract()
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        novel_info = soup.select_one(".novel-info")
        for e in novel_info:
            if e.text.strip().startswith("Author: "):
                self.novel_author = e.replace("Author: ", "").strip()
                logger.info("Novel author: %s", self.novel_author)
                break

        # possible_synopsis = soup.select_one(".entry-content")
        # if possible_synopsis:
        #     self.novel_synopsis = self.cleaner.extract_contents(possible_synopsis)
        # logger.info("Novel synopsis: %s", self.novel_synopsis)

        self.novel_tags = [
            a.text.split(" (")[0].strip() for a in soup.select("a.series-tag")
        ]
        logger.info("Novel tags: %s", self.novel_tags)

        possible_image = soup.select_one(".novel-cover img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["data-breeze"])
        logger.info("Novel cover: %s", self.novel_cover)

        volumes = set([])
        for a in soup.select(".chapter-item a"):
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

    def login(self, email, password):
        self.password = password

    def download_chapter_body(self, chapter):
        chapter_url = chapter["url"]
        soup = self.get_soup(chapter_url, encoding="utf8")

        if soup.select_one("#site-pass"):
            soup = self.submit_form_for_soup(
                url=self.absolute_url(chapter_url),
                headers={"Content-Encoding": "utf8"},
                data={
                    "site-pass": self.password,
                    "nonce-site-pass": soup.select_one("#nonce-site-pass")["value"],
                    "_wp_http_referer": urlparse(chapter_url).path,
                },
                encoding="utf8",
            )

        bads = ["chrysanthemumgarden (dot) com", "Chrysanthemum Garden"]

        contents = []
        for p in soup.select("#novel-content p"):
            for span in p.select('span[style*="width:0"]'):
                span.extract()

            if any(x in p.text for x in bads):
                continue

            text = ""
            for span in p.select("span.jum"):
                try:
                    text += self.descramble_text(span.text) + " "
                except IndexError:
                    pass

            if not text:
                text = p.text.strip()

            if not text:
                continue

            contents.append(text)

        return "<p>" + "</p><p>".join(contents) + "</p>"

    def descramble_text(self, cipher: str):
        plain = ""
        lower_fixer = "tonquerzlawicvfjpsyhgdmkbx"
        upper_fixer = "JKABRUDQZCTHFVLIWNEYPSXGOM"
        for ch in cipher.strip():
            if ch.islower():
                plain += lower_fixer[ord(ch) - ord("a")]
            elif ch.isupper():
                plain += upper_fixer[ord(ch) - ord("A")]
            else:
                plain += ch
        return plain
