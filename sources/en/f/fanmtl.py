# -*- coding: utf-8 -*-
import logging
from typing import Generator
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter
from lncrawl.templates.browser.chapter_only import ChapterOnlyBrowserTemplate

logger = logging.getLogger(__name__)


class FanMTLCrawler(ChapterOnlyBrowserTemplate):
    has_mtl = True
    base_url = "https://www.fanmtl.com/"

    def initialize(self):
        self.init_executor(1)
        self.cleaner.bad_css.update(
            {
                'div[align="center"]',
            }
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        possible_title = soup.select_one(".novel-info .novel-title")
        assert possible_title, "No novel title"
        return possible_title.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        possible_image = soup.select_one(".novel-header figure.cover img")
        if possible_image:
            return self.absolute_url(possible_image["src"])

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        possible_author = soup.select_one('.novel-info .author span[itemprop="author"]')
        if possible_author:
            yield possible_author.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        last_page = soup.select('.pagination a[data-ajax-update="#chpagedlist"]')[-1]
        last_page_url = self.absolute_url(last_page["href"])
        common_page_url = last_page_url.split("?")[0]
        params = parse_qs(urlparse(last_page_url).query)
        page_count = int(params["page"][0]) + 1
        futures = []
        for page in range(page_count):
            page_url = f"{common_page_url}?page={page}&wjm={params['wjm'][0]}"
            futures.append(self.executor.submit(self.get_soup, page_url))
        for soup in self.resolve_futures(futures, desc="TOC", unit="page"):
            yield from soup.select("ul.chapter-list li a")

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            url=self.absolute_url(tag["href"]),
            title=tag.select_one(".chapter-title").text.strip(),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one("#chapter-article .chapter-content")
