# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

novel_search_url = "%smodules/article/search.php"
cover_image_url = "%sfiles/article/image/%s/%s/%ss.jpg"


class PiaoTian(Crawler):
    base_url = [
        "https://www.piaotian.com",
        "https://www.ptwxz.com",
        "https://www.piaotia.com"
    ]

    def read_novel_info(self):
        # Transform bookinfo page into chapter list page
        # https://www.piaotia.com/bookinfo/8/8866.html -> https://www.piaotia.com/html/8/8866/
        if self.novel_url.startswith("%sbookinfo/" % self.home_url):
            self.novel_url = self.novel_url.replace("/bookinfo/", "/html/").replace(".html", "/")

        if self.novel_url.endswith("index.html"):
            self.novel_url = self.novel_url.replace("/index.html", "/")

        soup = self.get_soup(self.novel_url, encoding="gbk")

        self.novel_title = soup.select_one("div.title").text.replace("最新章节", "").strip()
        logger.info("Novel title: %s", self.novel_title)

        author = soup.select_one("div.list")
        author.select_one("a").decompose()
        self.novel_author = author.text.replace("作者：", "").strip()
        logger.info("Novel author: %s", self.novel_author)

        ids = self.novel_url.replace("%shtml/" % self.home_url, "").split("/")
        logger.debug(self.home_url)
        self.novel_cover = cover_image_url % (self.home_url, ids[0], ids[1], ids[1])
        logger.info("Novel cover: %s", self.novel_cover)

        for a in soup.select("div.centent ul li a"):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text,
                    "url": self.novel_url + a["href"],
                }
            )

    def download_chapter_body(self, chapter):
        headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9"}
        raw_html = self.get_response(chapter.url, headers=headers)
        raw_html.encoding = "gbk"
        raw_text = raw_html.text.replace('<script language="javascript">GetFont();</script>', '<div id="content">')
        self.last_soup_url = chapter.url
        soup = self.make_soup(raw_text)

        body = soup.select_one("div#content")
        for elem in body.select("h1, script, div, table"):
            elem.decompose()

        text = self.cleaner.extract_contents(body)

        return text
