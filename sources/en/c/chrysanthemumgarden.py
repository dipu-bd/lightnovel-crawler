# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

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
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        # self.novel_author = soup.select_one('.bookinfo .status').text
        # logger.info('%s', self.novel_author)

        possible_image = soup.select_one(".novel-cover img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
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

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        bads = ["chrysanthemumgarden (dot) com", "Chrysanthemum Garden"]

        contents = []
        for p in soup.select("#novel-content p"):
            for span in p.select('span[style*="width:0"]'):
                span.extract()

            if any(x in p.text for x in bads):
                continue

            text = ""
            for span in p.select("span.jum"):
                text += self.descramble_text(span.text) + " "

            if not text:
                text = p.text.strip()

            if not text:
                continue

            contents.append(text)

        return "<p>" + "</p><p>".join(contents) + "</p>"

    def descramble_text(self, cipher):
        plain = ""
        lower_fixer = "tonquerzlawicvfjpsyhgdmkbx"
        upper_fixer = "JKABRUDQZCTHFVLIWNEYPSXGOM"
        for ch in cipher.strip():
            if not ch.isalpha():
                plain += ch
            elif ch.islower():
                plain += lower_fixer[ord(ch) - ord("a")]
            elif ch.isupper():
                plain += upper_fixer[ord(ch) - ord("A")]
            else:
                plain += ch
        return plain
