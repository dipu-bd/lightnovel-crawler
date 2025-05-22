# -*- coding: utf-8 -*-
import logging
import re
from bs4 import Tag
from lncrawl.core.crawler import Crawler
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
    "application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,de-CH;q=0.8,de;q=0.7",
    "Cache-Control": "no-cache",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.69shu.pro",
    "DNT": "1",
    "Referer": "https://www.69shu.pro/modules/article/search.php",
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
search_url = "https://www.69shuba.com/modules/article/search.php"


class sixnineshu(Crawler):
    base_url = [
        "https://www.69shuba.com/",
        "https://www.69shu.com/",
        "https://www.69xinshu.com/",
        "https://www.69shu.pro/",
        "https://www.69shuba.pro/",
    ]

    def initialize(self):
        # the default lxml parser cannot handle the huge gbk encoded sites (fails after 4.3k chapters)
        self.init_parser("html.parser")
        self.init_executor(ratelimit=20)

    def search_novel(self, query):
        query = urllib.parse.quote(query.encode("gbk"))
        data = f"searchkey={query}&submit=Search"
        soup = self.post_soup(
            search_url,
            headers=headers,
            data=data,
            encoding="gbk",
            # cookies=self.cookies2,
        )

        results = []
        for novel in soup.select("div.newbox ul li"):
            results.append(
                {
                    "title": novel.select_one("h3 a:not([imgbox])").text.title(),
                    "url": self.absolute_url(novel.select_one("a")["href"]),
                    "info": "Latest: %s" % novel.select_one("div.zxzj p").text,
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url, encoding="gbk")

        possible_title = soup.select_one("div.booknav2 h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("div.bookimg2 img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select_one('.booknav2 p a[href*="author"]')
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info("Novel Author: %s", self.novel_author)

        # tags are in a script tag and js add them to the page
        match = re.search(r"tags:\s*'([^']+)'", str(soup))
        if match:
            tags = match.group(1)
            self.novel_tags = [tag.strip() for tag in tags.split("|") if tag.strip()]
        possible_tags = soup.select('.booknav2 p a[href*="/class/"]')
        for tag in possible_tags:
            self.novel_tags.append(tag.text.strip())

        logger.info("Novel Tags: %s", self.novel_tags)

        possible_synopsis = soup.select_one("div.navtxt")
        if isinstance(possible_synopsis, Tag):
            self.novel_synopsis = self.cleaner.extract_contents(possible_synopsis)
        logger.info("Novel Synopsis: %s", self.novel_synopsis)

        # Only one category per novel on this website
        possible_tag = soup.select_one('.booknav2 p a[href*="top"]')
        if isinstance(possible_tag, Tag):
            self.novel_tags = [possible_tag.text.strip()]
        logger.info("Novel Tag: %s", self.novel_tags)

        # https://www.69shuba.com/txt/A43616.htm -> https://www.69shuba.com/A43616/
        soup = self.get_soup(
            self.novel_url.replace("/txt/", "/").replace(".htm", "/"), encoding="gbk"
        )

        volumes = set([])
        for li in soup.select("div#catalog ul li"):
            a = li.select_one("a")
            assert isinstance(a, Tag)
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

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url, encoding="gbk")

        contents = soup.select_one("div.txtnav")
        contents.select_one("h1").decompose()
        contents.select_one("div.txtinfo").decompose()
        contents.select_one("div#txtright").decompose()

        return self.cleaner.extract_contents(contents)
