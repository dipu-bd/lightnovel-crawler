import re
from typing import Iterable
from urllib.parse import quote_plus

from bs4 import BeautifulSoup, Tag

from ..core.exeptions import LNException
from ..models import Chapter, SearchResult
from .soup.chapter_only import ChapterOnlySoupTemplate
from .soup.searchable import SearchableSoupTemplate


class NovelFullTemplate(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    is_template = True

    def get_search_page_soup(self, query: str) -> BeautifulSoup:
        return self.get_soup(
            f"{self.home_url}search?keyword={quote_plus(query.lower())}"
        )

    def select_search_items(self, soup: BeautifulSoup) -> Iterable[Tag]:
        return soup.select("#list-page .row h3[class*='title'] > a")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        title = tag.get("title", tag.get_text())
        return SearchResult(
            title=title.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one("h3.title")
        assert tag
        self.novel_title = tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".book img")
        assert tag
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup):
        possible_selectors = [
            "a[href*='/a/']",
            "a[href*='/au/']",
            "a[href*='/authors/']",
            "a[href*='/author/']",
        ]
        for a in soup.select_one(".info").select(",".join(possible_selectors)):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup):
        nl_id_tag = soup.select_one("#rating[data-novel-id]")
        if not isinstance(nl_id_tag, Tag):
            raise LNException("No novel_id found")

        nl_id = nl_id_tag["data-novel-id"]
        script = soup.find("script", text=re.compile(r"ajaxChapterOptionUrl\s+="))
        if isinstance(script, Tag):
            url = f"{self.home_url}ajax-chapter-option?novelId={nl_id}"
        else:
            url = f"{self.home_url}ajax/chapter-archive?novelId={nl_id}"

        soup = self.get_soup(url)
        yield from soup.select("ul.list-chapter > li > a[href], select > option[value]")

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag.get("href") or tag.get("value")),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one("#chr-content, #chapter-content")
