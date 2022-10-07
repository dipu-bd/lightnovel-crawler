# -*- coding: utf-8 -*-
import logging
from typing import Iterable
from urllib.parse import quote_plus

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate

logger = logging.getLogger(__name__)


class ReadLightNovelsNet(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    base_url = [
        "https://readlightnovels.net/",
    ]

    def get_search_page_soup(self, query: str) -> BeautifulSoup:
        return self.get_soup(f"{self.home_url}?s={quote_plus(query)}")

    def select_search_items(self, soup: BeautifulSoup) -> Iterable[Tag]:
        return soup.select(".home-truyendecu")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        a = tag.select_one("a")
        if not a:
            return
        latest = tag.select_one(".caption .label-primary")
        if latest:
            latest = latest.text.strip()
        return SearchResult(
            title=a["title"].strip(),
            url=self.absolute_url(a["href"]),
            info=f"Latest chapter: {latest}",
        )

    def parse_title(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one(".title")
        assert isinstance(tag, Tag), "No title found"
        self.novel_title = " ".join(
            [str(x) for x in tag.contents if isinstance(x, str)]
        )

    def parse_cover(self, soup: BeautifulSoup):
        tag = soup.select_one(".book img[src]")
        if not isinstance(tag, Tag):
            return
        self.novel_cover = self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup):
        self.novel_author = ", ".join([a.text.strip() for a in soup.select(".info a")])

    def select_chapter_tags(self, soup: BeautifulSoup):
        novel_id = soup.select_one("#id_post")["value"]
        logger.info(f"Novel id: {novel_id}")

        resp = self.submit_form(
            f"{self.home_url}wp-admin/admin-ajax.php",
            {
                "action": "tw_ajax",
                "type": "list_chap",
                "id": novel_id,
            },
        )
        soup = self.make_soup(resp)
        yield from soup.select("option")

    def parse_chapter_item(self, id: int, tag: Tag, soup: BeautifulSoup) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag["value"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".chapter-content")
