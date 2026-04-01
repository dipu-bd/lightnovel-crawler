# -*- coding: utf-8 -*-
import logging
from typing import Generator, Optional
from urllib.parse import parse_qs, urlparse

from lncrawl.core import Chapter, PageSoup
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

    def parse_title(self, soup: PageSoup) -> str:
        possible_title = soup.select_one(".novel-info .novel-title")
        assert possible_title, "No novel title"
        return possible_title.text.strip()

    def parse_cover(self, soup: PageSoup) -> Optional[str]:
        possible_image = soup.select_one(".novel-header figure.cover img")
        if not possible_image:
            return None
        src = possible_image.get("data-src") or possible_image["src"]
        return self.absolute_url(src)

    def parse_authors(self, soup: PageSoup) -> Generator[str, None, None]:
        possible_author = soup.select_one('.novel-info .author span[itemprop="author"]')
        if possible_author:
            yield possible_author.text.strip()

    def select_chapter_tags(self, soup: PageSoup) -> Generator[PageSoup, None, None]:
        all_pages = soup.select('.pagination a[data-ajax-update="#chpagedlist"]')
        if not all_pages:
            yield from soup.select("ul.chapter-list li a")
            return

        last_page_url = self.absolute_url(all_pages[-1]["href"])
        common_page_url = last_page_url.split("?")[0]
        params = parse_qs(urlparse(last_page_url).query)
        page_count = int(params["page"][0]) + 1

        futures = [
            self.executor.submit(self.get_soup, f"{common_page_url}?page={page}&wjm={params['wjm'][0]}")
            for page in range(page_count)
        ]
        for page in self.resolve_futures(futures, desc="TOC", unit="page"):
            if page:
                yield from page.select("ul.chapter-list li a")

    def parse_chapter_item(self, tag: PageSoup, id: int) -> Chapter:
        chapter_title = tag.select_one(".chapter-title")
        assert chapter_title, "No chapter title"
        return Chapter(
            id=id,
            url=self.absolute_url(tag["href"]),
            title=chapter_title.get_text(strip=True),
        )

    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        return soup.select_one("#chapter-article .chapter-content")
