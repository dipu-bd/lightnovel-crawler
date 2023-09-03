# -*- coding: utf-8 -*-
import logging
from bs4 import Tag
from lncrawl.core.crawler import Crawler
import urllib.parse

import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.69shu.com",
    "DNT": "1",
    "Alt-Used": "www.69shu.com",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}

logger = logging.getLogger(__name__)
search_url = "https://www.69shu.com/modules/article/search.php"


class sixnineshu(Crawler):
    base_url = "https://www.69shu.com/"

    def get_soup(self, url):
        """overwrite the get_soup function to set the encoding"""
        data = requests.get(url, headers=headers)
        data.encoding = "gbk"
        soup = BeautifulSoup(data.text, "html.parser")
        return soup

    def search_novel(self, query):
        query = urllib.parse.quote(query.encode("gbk"))
        data = requests.post(
            "https://www.69shu.com/modules/article/search.php",
            headers=headers,
            data=f"searchkey={query}&searchtype=all",
        )
        data.encoding = "gbk"

        soup = BeautifulSoup(data.text, "html.parser")

        # If only one result is found, we will be redirected to the novel page
        # We can check the URL to see if we are redirected or not

        redirected = data.url != search_url

        if not redirected:
            results = []
            for novel in soup.select("div.newbox ul li"):
                results.append(
                    {
                        "title": novel.select_one("h3 a").text.title(),
                        "url": novel.select_one("a")["href"],
                        "info": "Latest: %s" % novel.select_one("div.zxzj p").text,
                    }
                )

        else:
            results = [
                {
                    "title": soup.select_one("div.booknav2 h1").text.strip(),
                    "url": data.url,
                    "info": "Latest: %s" % soup.select_one("div.qustime ul li").text,
                }
            ]

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("div.booknav2 h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("div.bookimg2 img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select_one('.booknav2 p a[href*="authorarticle"]')
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info("Novel Author: %s", self.novel_author)

        possible_synopsis = soup.select_one("div.navtxt p")
        if isinstance(possible_synopsis, Tag):
            self.novel_synopsis = possible_synopsis.text.strip()
        logger.info("Novel Synopsis: %s", self.novel_synopsis)

        # Only one category per novel on this website
        possible_tag = soup.select_one('.booknav2 p a[href*="top"]')
        if isinstance(possible_tag, Tag):
            self.novel_tags = [possible_tag.text.strip()]
        logger.info("Novel Tag: %s", self.novel_tags)

        # https://www.69shu.com/txt/A43616.htm -> https://www.69shu.com/A43616/
        soup = self.get_soup(self.novel_url.replace("/txt/", "/").replace(".htm", "/"))

        for li in soup.select("div.catalog ul li"):
            chap_id = int(li["data-num"])
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": li.text.strip(),
                    "url": self.absolute_url(li.select_one("a")["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.txtnav")
        contents.select_one("h1").decompose()
        contents.select_one("div.txtinfo").decompose()
        contents.select_one("div#txtright").decompose()

        return self.cleaner.extract_contents(contents)
