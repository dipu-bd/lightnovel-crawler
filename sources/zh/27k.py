# -*- coding: utf-8 -*-
import logging
from bs4 import Tag
from lncrawl.core.crawler import Crawler
import urllib.parse

from lncrawl.models import Volume, Chapter

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, utf-8",
    "Accept-Language": "en-US,en;q=0.9,de-CH;q=0.8,de;q=0.7",
    "Cache-Control": "no-cache",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://so.27k.net/",
    "DNT": "1",
    "Referer": "https://so.27k.net/search",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Opera GX";v="106"',
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}

logger = logging.getLogger(__name__)
search_url = "https://so.27k.net/search/"


class LeYueDu(Crawler):
    base_url = [
        "https://so.27k.net",
        "https://www.27k.net",
        "https://m.27k.net",
        "https://tw.27k.net",
        "https://www.lreads.com",
    ]

    def initialize(self):
        self.init_parser("html.parser")
        self.init_executor(ratelimit=20)

    def search_novel(self, query):
        query = urllib.parse.quote(query)
        data = f"searchkey={query}&searchtype=all"
        soup = self.post_soup(
            search_url,
            headers=headers,
            data=data,
        )

        results = []
        for novel in soup.select("div.newbox ul li"):
            results.append(
                {
                    "title": novel.select_one("h3 a:not([imgbox])").text.title(),
                    "url": self.absolute_url(novel.select_one("h3 a")["href"]),
                    "info": "Latest: %s" % novel.select_one("div.zxzj p").text.replace("最近章节", "").replace("最近章節", ""),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("div.booknav2 h1 a")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("div.bookimg2 img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select_one('.booknav2 p a[href*="/author/"]')
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info("Novel Author: %s", self.novel_author)

        # Only one category per novel on this website
        possible_tag = soup.select_one('.booknav2 p a[href*="/sort/"]')
        if isinstance(possible_tag, Tag):
            self.novel_tags = [possible_tag.text.strip()]
        logger.info("Novel Tag: %s", self.novel_tags)

        # https://www.27k.net/book/70154.html -> https://www.27k.net/read/70154/
        soup = self.get_soup(self.novel_url.replace("/book/", "/read/").replace(".html", "/"))

        # Synopsis in chapter list page is cleaner than in book info page
        possible_synopsis = soup.select_one("div.newnav .ellipsis_2")
        if isinstance(possible_synopsis, Tag):
            self.novel_synopsis = possible_synopsis.text.strip()
        logger.info("Novel Synopsis: %s", self.novel_synopsis)

        chapter_list = soup.select("div#catalog ul li")

        for item in chapter_list:
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append(Volume(vol_id))
            a = item.a["href"]
            self.chapters.append(
                Chapter(
                    chap_id,
                    url=self.absolute_url(a),
                    title=item.a.text.strip(),
                    volume=vol_id,
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url)

        contents = soup.select_one("div.txtnav")
        contents.select_one("h1").decompose()
        contents.select_one("div.txtinfo").decompose()
        contents.select_one("div#txtright").decompose()
        for elem in contents.select("div.baocuo"):
            elem.decompose()

        return self.cleaner.extract_contents(contents)
