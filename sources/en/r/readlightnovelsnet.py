# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlencode

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate

logger = logging.getLogger(__name__)


class ReadLightNovelsNet(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    base_url = [
        "https://readlightnovels.net/",
    ]

    def select_search_items(self, query: str):
        params = {"s": query}
        soup = self.get_soup(f"{self.home_url}?{urlencode(params)}")
        yield from soup.select(".home-truyendecu")

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

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".title")
        assert tag
        return " ".join([str(x) for x in tag.contents if isinstance(x, str)])

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".book img[src]")
        assert tag
        return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup):
        for a in soup.select(".info a"):
            yield a.text.strip()

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

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag["value"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".chapter-content")
