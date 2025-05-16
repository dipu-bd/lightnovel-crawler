# -*- coding: utf-8 -*-

import logging
import re
from typing import List
from urllib.parse import quote_plus, urlencode

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException
from lncrawl.models import Chapter, SearchResult

logger = logging.getLogger(__name__)


class NoveLightCrawler(Crawler):
    base_url = "https://novelight.net/"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(["div.advertisment"])

    def search_novel(self, query) -> List[SearchResult]:
        soup = self.get_soup(
            f"{self.home_url}catalog/?search={quote_plus(query.lower())}"
        )

        return [
            SearchResult(title=a.text.strip(), url=self.absolute_url(a["href"]))
            for a in soup.select(".manga-grid-list a.item")
            if isinstance(a, Tag)
        ]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        title_tag = soup.select_one("header.header-manga h1")
        if not isinstance(title_tag, Tag):
            raise LNException("No title found")
        self.novel_title = title_tag.get_text().strip()
        logger.info("Novel title: %s", self.novel_title)

        novel_cover = soup.select_one("div.second-information div.poster img")
        if isinstance(novel_cover, Tag):
            self.novel_cover = self.absolute_url(novel_cover["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        novel_synopsis = soup.select_one("div#information section.text-info")
        if isinstance(novel_synopsis, Tag):
            self.novel_synopsis = self.cleaner.extract_contents(novel_synopsis)

        novel_tags = soup.select(
            "div#information section.tags a[href^='/catalog/?tags=']"
        )
        for tag in novel_tags:
            self.novel_tags.append(tag.get_text().strip())

        novel_author = soup.select_one(".mini-info a[href^='/character/'] div.info")
        if isinstance(novel_author, Tag) and novel_author.get_text():
            self.novel_author = novel_author.get_text().strip()
        logger.info("Novel author: %s", self.novel_author)

        page_scripts = soup.select("body > script:not([src])")
        scripts_joined = "\n".join(str(s) for s in page_scripts)
        book_id = re.search(r'.*const BOOK_ID = "(\d+)".*', scripts_joined).group(1)
        if not book_id:
            raise LNException("Could not extract book_id from novel page")
        logger.debug("book_id: %s", book_id)
        # this is different token than the 'csrftoken' in cookies
        csrfmiddlewaretoken = re.search(
            r'.*window.CSRF_TOKEN = "(\w+)".*', scripts_joined
        ).group(1)
        if not csrfmiddlewaretoken:
            raise LNException("Could not extract csrfmiddlewaretoken from novel page")
        logger.debug("csrfmiddlewaretoken: %s", csrfmiddlewaretoken)

        headers = {
            "Accept": "*/*",
            "Referer": self.novel_url,
            "x-requested-with": "XMLHttpRequest",
        }
        chapters_lists = soup.select("select#select-pagination-chapter > option")
        bar = self.progress_bar(
            total=len(chapters_lists), desc="Chapters list", unit="page"
        )
        encountered_paid_chapter = False
        for page in reversed(chapters_lists):
            if encountered_paid_chapter:
                break
            params = {
                "csrfmiddlewaretoken": csrfmiddlewaretoken,
                "book_id": book_id,
                "page": page["value"],
            }
            chapters_response = self.get_json(
                f"{self.home_url}book/ajax/chapter-pagination?{urlencode(params)}",
                headers=headers,
            )
            chapters_soup = self.make_soup(chapters_response["html"])
            for a in reversed(chapters_soup.select("a[href^='/book/chapter/']")):
                if a.select_one(".chapter-info .cost"):
                    encountered_paid_chapter = True
                    break
                else:
                    self.chapters.append(
                        Chapter(
                            id=len(self.chapters) + 1,
                            title=a.select_one(".title").text.strip(),
                            url=self.absolute_url(a["href"]),
                        )
                    )
            bar.update()
        bar.close()
        if encountered_paid_chapter:
            logger.warning(
                "WARNING: Paid chapters are not supported and will be skipped."
            )

    def download_chapter_body(self, chapter: Chapter):
        soup = self.get_soup(chapter.url)
        contents = soup.select_one(".chapter-text")
        self.cleaner.clean_contents(contents)

        return str(contents)
