# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core import Chapter, LegacyCrawler, SearchResult
from lncrawl.exceptions import LNException

logger = logging.getLogger(__name__)


class DdxSss(LegacyCrawler):
    base_url = [
        "https://www.ddxss.cc/",
        "https://www.ddtxt8.cc/",
    ]

    def initialize(self):
        self.init_executor(ratelimit=20)

        # the default lxml parser cannot handle the huge gbk encoded sites (fails after 4.3k chapters)
        self.parser = "html.parser"
        self.cleaner.bad_tags.update(["script", "a"])
        self.cleaner.bad_css.update(
            [
                ".noshow",
                "div.Readpage.pagedown",
            ]
        )

        # p tags should only show up after being parsed and formatted the first time
        self.cleaner.bad_tag_text_pairs["p"] = [
            "请收藏本站：",
            "顶点小说手机版：",
            "您可以在百度里搜索",
            "最新章节地址：",
            "全文阅读地址：",
            "txt下载地址：",
            "手机阅读：",
            '为了方便下次阅读，你可以点击下方的"收藏"记录本次',
            "请向你的朋友（QQ、博客、微信等方式）推荐本书，谢谢您的支持！！",
        ]

    def search_novel(self, query):
        data = self.get_json(
            f"{self.scraper.origin}user/search.html?q={query}",
            # if this cookie "expires" it might return INT results again -> maybe remove search functionality
            cookies={"hm": "7c2cee175bfbf597f805ebc48957806e"},
        )
        if isinstance(data, int):
            logger.info("Failed to get any results, likely auth failure")
            return []

        results = []
        for book in data:
            results.append(
                SearchResult(
                    title=book["articlename"],
                    url=self.absolute_url(book["url_list"]),
                    info=f"Author: {book['author']} | Synopsis: {book['intro']}",
                )
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        match = re.match(re.compile("http.+/book/(\\d+).*"), self.novel_url)
        if not match:
            raise LNException("No book id found")
        book_id = int(match[1])
        soup = self.get_soup(self.novel_url, encoding="utf-8")

        meta = soup.select_one(".book > .info")

        possible_title = meta.select_one("h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = meta.select_one(".cover > img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = meta.find(".small span", text=r"作者：")
        if possible_author:
            self.novel_author = possible_author.text.strip().replace("作者：", "")
        logger.info("Novel Author: %s", self.novel_author)

        possible_synopsis = meta.select_one(".intro")
        if possible_synopsis:
            self.novel_synopsis = possible_synopsis.text.strip()
        logger.info("Novel Synopsis: %s", self.novel_synopsis)

        for a in soup.select("div.listmain a"):
            if not a:
                continue  # Skipping fake anchor
            if str(book_id) not in a["href"]:
                continue  # Skipping non-chapter link

            self.chapters.append(
                Chapter(
                    id=len(self.chapters) + 1,
                    url=self.absolute_url(a["href"]),
                    title=a.text.strip(),
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url, encoding="utf-8")
        contents = soup.select_one("div#chaptercontent")
        text = self.cleaner.extract_contents(contents)
        # chapter title is usually present but without space between chapter X and the title
        text = text.replace(chapter.title, "")
        text = text.replace(chapter.title.replace(" ", ""), "")
        # remove paragraphs with bad text after parsing linebreaks
        text = self.cleaner.extract_contents(self.make_soup(text))
        return text
