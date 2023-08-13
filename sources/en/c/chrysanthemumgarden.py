# -*- coding: utf-8 -*-
import logging

from requests import Response

from lncrawl.core.crawler import Crawler
import requests

logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "multipart/form-data; boundary=---------------------------371654104016101047241770203416",
    "Origin": "https://chrysanthemumgarden.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://chrysanthemumgarden.com/novel-tl/ygbg/ygbg-153/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}


class ChrysanthemumGarden(Crawler):
    base_url = "https://chrysanthemumgarden.com/"

    def submit_form(self, url, data=None) -> Response:
        return requests.post(url, headers=headers, data=data)

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
        #     self.novel_synopsis = self.cleaner.extract_contents(
        #         possible_synopsis
        #     )
        # logger.info("Novel synopsis: %s", self.novel_synopsis)

        self.novel_tags = [
            a.text.split(" (")[0].strip() for a in soup.select("a.series-tag")
        ]
        logger.info("Novel tags: %s", self.novel_tags)

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

    def login(self, email, password):
        self.password = password

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        if soup.select_one("#site-pass"):
            nonce = soup.select_one("#nonce-site-pass")["value"]
            data = f'-----------------------------371654104016101047241770203416\r\nContent-Disposition: form-data; name="site-pass"\r\n\r\n{self.password}\r\n-----------------------------371654104016101047241770203416\r\nContent-Disposition: form-data; name="nonce-site-pass"\r\n\r\n{nonce}\r\n-----------------------------371654104016101047241770203416\r\n'  # noqa: E501

            soup = self.make_soup(
                self.submit_form(
                    url=self.absolute_url(chapter["url"]), 
                    data=data
                ),
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
