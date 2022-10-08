# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote

from bs4 import ResultSet, Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException
from lncrawl.models import Chapter, SearchResult

logger = logging.getLogger(__name__)


class Novel35Crawler(Crawler):
    base_url = ["https://novel35.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            ['div[align="left"]', 'img[src*="proxy?container=focus"]']
        )

    def search_novel(self, query):
        soup = self.get_soup(f"{self.home_url}search?keyword={quote(query)}")
        results = []
        for div in soup.select("#list-page .archive .list-truyen > .row"):
            a = div.select_one(".truyen-title a")
            info = div.select_one(".text-info a .chapter-text")
            results.append(
                SearchResult(
                    title=a.text.strip(),
                    url=self.absolute_url(a["href"]),
                    info=info.text.strip() if isinstance(info, Tag) else "",
                )
            )
        return results

    def read_novel_info(self):
        self.novel_url = self.novel_url.split("?")[0].strip("/")
        soup = self.get_soup(self.novel_url)

        title_tag = soup.select_one("h1.title")
        if not isinstance(title_tag, Tag):
            raise LNException("No title found")

        self.novel_title = title_tag.text.strip()

        image_tag = soup.select_one(".info-holder .book img")
        if isinstance(image_tag, Tag):
            self.novel_cover = self.absolute_url(image_tag["src"])

        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = ", ".join(
            [
                a.text.strip()
                for a in soup.select(".info-holder .info a[href^='/author/']")
                if isinstance(a, Tag)
            ]
        )

        logger.info("Novel author: %s", self.novel_author)

        pagination_link = soup.select("#list-chapter ul.pagination a:not([rel])")
        page_count = (
            int(pagination_link[-1].get_text())
            if isinstance(pagination_link, ResultSet)
            else 1
        )
        logger.info("Chapter list pages: %d" % page_count)

        for page in range(1, page_count + 1):
            url = f"{self.novel_url}?page={page}"
            soup = self.get_soup(url)
            for a in soup.select("ul.list-chapter li a"):
                self.chapters.append(
                    Chapter(
                        id=len(self.chapters) + 1,
                        title=a["title"].strip(),
                        url=self.absolute_url(a["href"]),
                    )
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div#chapter-content")
        return self.cleaner.extract_contents(contents)
