# -*- coding: utf-8 -*-
import time
from concurrent.futures import Future
from typing import List
from urllib.parse import parse_qs, urlencode, urlparse

from bs4 import BeautifulSoup, Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException
from lncrawl.models import SearchResult


class NovelMTLTemplate(Crawler):
    is_template = True

    def initialize(self) -> None:
        self.cur_time = int(1000 * time.time())

    def search_novel(self, query) -> List[SearchResult]:
        soup = self.get_soup(f"{self.home_url}search.html")
        form = soup.select_one('.search-container form[method="post"]')
        assert isinstance(form, Tag), "No search form"

        action_url = self.absolute_url(form["action"])
        payload = {input["name"]: input["value"] for input in form.select("input")}
        payload["keyboard"] = query
        response = self.submit_form(action_url, payload)
        soup = self.make_soup(response)

        return [
            self.parse_search_item(a)
            for a in soup.select("ul.novel-list .novel-item a")[:10]
        ]

    def parse_search_item(self, tag: Tag) -> SearchResult:
        title = tag.select_one(".novel-title").text.strip()
        return SearchResult(
            title=title,
            url=self.absolute_url(tag["href"]),
            info=" | ".join([x.text.strip() for x in tag.select(".novel-stats")]),
        )

    def read_novel_info(self) -> None:
        soup = self.get_soup(self.novel_url)
        self.parse_title(soup)
        self.parse_image(soup)
        self.parse_authors(soup)
        self.parse_chapter_list(soup)

    def parse_title(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one(".novel-info .novel-title")
        if not isinstance(tag, Tag):
            raise LNException("No title found")
        self.novel_title = tag.text.strip()

    def parse_image(self, soup: BeautifulSoup):
        tag = soup.select_one("#novel figure.cover img")
        if isinstance(tag, Tag):
            if tag.has_attr("data-src"):
                self.novel_cover = self.absolute_url(tag["data-src"])
            elif tag.has_attr("src"):
                self.novel_cover = self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup):
        self.novel_author = ", ".join(
            [
                a.text.strip()
                for a in soup.select('.novel-info .author span[itemprop="author"]')
            ]
        )

    def parse_chapter_list(self, soup: BeautifulSoup) -> BeautifulSoup:
        last_page = soup.select("#chapters .pagination li a")[-1]["href"]
        last_page_qs = parse_qs(urlparse(last_page).query)
        max_page = int(last_page_qs["page"][0])
        wjm = last_page_qs["wjm"][0]

        futures: List[Future] = []
        for i in range(max_page + 1):
            payload = {
                "page": i,
                "wjm": wjm,
                "_": self.cur_time,
                "X-Requested-With": "XMLHttpRequest",
            }
            url = f"{self.home_url}e/extend/fy.php?{urlencode(payload)}"
            futures.append(self.executor.submit(self.get_soup, url))

        for page, f in enumerate(futures):
            soup = f.result()
            vol_id = page + 1
            self.volumes.append({"id": vol_id})
            for a in soup.select("ul.chapter-list li a"):
                chap_id = len(self.chapters) + 1
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": vol_id,
                        "url": self.absolute_url(a["href"]),
                        "title": a.select_one(".chapter-title").text.strip(),
                    }
                )

    def download_chapter_body(self, chapter) -> None:
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".chapter-content")
        return self.cleaner.extract_contents(contents)
