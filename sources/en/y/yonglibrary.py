# -*- coding: utf-8 -*-
import logging
from typing import Generator, List, Union

from lncrawl.core import Chapter, PageSoup, SearchResult, Volume
from lncrawl.templates.browser.general import GeneralBrowserTemplate

logger = logging.getLogger(__name__)


class YongLibraryCrawler(GeneralBrowserTemplate):
    base_url = [
        "https://yonglibrary.com/",
    ]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                ".ad-slot",
                ".chapter-companion",
                ".chapter-content__badge",
                "script",
            ]
        )
        self.cleaner.bad_text_regex.update(
            [
                r"window.pubfuturetag = .*})",
            ]
        )

    def search_novel(self, query: str) -> List[SearchResult]:
        url = f"{self.home_url}wp-json/wp/v2/search"
        params = {"search": query, "per_page": 10, "type": "term", "subtype": "category"}
        data = self.get_json(url, params=params)
        results = []
        for item in data:
            title = item.get("title", "")
            cat_url = item.get("url", "")
            novel_url = cat_url.replace("/category/", "/", 1)
            results.append(SearchResult(title=title, url=novel_url))
        return results

    def parse_title(self, soup: PageSoup) -> str:
        tag = soup.select_one("h1.novel-hero__title")
        assert tag, "Could not find novel title"
        return tag.get_text(strip=True)

    def parse_cover(self, soup: PageSoup) -> str:
        tag = soup.select_one(".novel-hero__cover img, img.novel-hero__image")
        if tag:
            return self.absolute_url(tag.get("src", ""))
        return ""

    def parse_genres(self, soup: PageSoup) -> Generator[str, None, None]:
        for tag in soup.select(".novel-hero__tags .badge--genre"):
            text = tag.get_text(strip=True)
            if text:
                yield text

    def parse_summary(self, soup: PageSoup) -> str:
        tag = soup.select_one(".insight-content")
        if tag:
            first_p = tag.find("p")
            if first_p:
                return first_p.get_text(strip=True)
            return tag.get_text(strip=True)
        return ""

    def parse_chapter_list(self, soup: PageSoup) -> Generator[Union[Chapter, Volume], None, None]:
        items = soup.select("li.chapter-item")
        items.reverse()
        for idx, item in enumerate(items):
            a = item.select_one("a.chapter-item__link")
            if not a:
                continue
            title_tag = item.select_one(".chapter-item__title")
            title = title_tag.get_text(strip=True) if title_tag else a.get_text(strip=True)
            yield Chapter(
                id=idx + 1,
                url=self.absolute_url(a["href"]),
                title=title,
            )

    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        return soup.select_one(".chapter-content__body")
