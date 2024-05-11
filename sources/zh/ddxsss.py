# -*- coding: utf-8 -*-
import logging
import re

from bs4 import Tag
from lncrawl.core.crawler import Crawler

from lncrawl.models import Volume, Chapter, SearchResult

logger = logging.getLogger(__name__)


class DdxSss(Crawler):
    base_url = [
        "https://www.ddxss.cc/",
    ]
    # custom banned text as it's all loose and the cleaner deletes the whole chapter if used in bad_text_*
    banned_text = [
        "请收藏本站：https://www.ddxsss.com。顶点小说手机版：https://m.ddxsss.com",
    ]

    def initialize(self):
        # the default lxml parser cannot handle the huge gbk encoded sites (fails after 4.3k chapters)
        self.init_parser("html.parser")
        self.cleaner.bad_tags.update(["script", "a"])
        self.cleaner.bad_css.update([
            ".noshow",
            "div.Readpage.pagedown",
        ])

    def search_novel(self, query):
        data = self.get_json(
            f"{self.home_url}user/search.html?q={query}",
            # if this cookie "expires" it might return INT results again -> maybe remove search functionality
            cookies={"hm": "7c2cee175bfbf597f805ebc48957806e"}
        )
        if isinstance(data, int):
            logger.warning("Failed to get any results, likely auth failure")
            return []

        results = []
        for book in data:
            results.append(
                SearchResult(
                    title=book["articlename"],
                    url=self.absolute_url(book["url_list"]),
                    info=f"Author: {book['author']} | Synopsis: {book['intro']}"
                )
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        book_id = int(re.match(re.compile("http.+/book/(\\d+).*"), self.novel_url)[1])
        soup = self.get_soup(self.novel_url, encoding="utf-8")

        meta = soup.select_one(".book > .info")

        possible_title = meta.select_one("h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = meta.select_one(".cover > img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = meta.find('.small span', text=r"作者：")
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip().replace("作者：", "")
        logger.info("Novel Author: %s", self.novel_author)

        possible_synopsis = meta.select_one(".intro")
        if isinstance(possible_synopsis, Tag):
            self.novel_synopsis = possible_synopsis.text.strip()
        logger.info("Novel Synopsis: %s", self.novel_synopsis)

        for idx, a in enumerate(soup.select("div.listmain a")):
            if not isinstance(a, Tag):
                logger.info("Skipping fake anchor? %s", a)
                continue
            if str(book_id) not in a["href"]:
                logger.info("Skipping non-chapter link: %s", a["href"])
                continue

            chap_id = int(re.match(re.compile(f".*/book/{book_id}/(\\d+).*"), a["href"])[1])
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append(Volume(vol_id))
            if not a:
                # this should not occur with html.parser, if it does, likely due to parser/encoding issue
                logger.warning("Failed to get Chapter %d! Missing Link", chap_id)
                continue
            self.chapters.append(
                Chapter(
                    chap_id,
                    url=self.absolute_url(a["href"]),
                    title=a.text.strip(),  # .replace(f"第{chap_id}章 ", ""),
                    volume=vol_id,
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url, encoding="utf-8")
        contents = soup.select_one("div#chaptercontent")
        text = self.cleaner.extract_contents(contents)
        for bad_text in self.banned_text:
            text = text.replace(bad_text, "")
        # chapter title is usually present but without space between chapter X and the title
        text = text.replace(chapter.title, "")
        text = text.replace(chapter.title.replace(" ", ""), "")
        return text
