import re
from typing import Generator, Iterable
from urllib.parse import quote_plus

from bs4 import BeautifulSoup, Tag

from ..core.exeptions import LNException
from ..models import Chapter, SearchResult
from .soup.paginated_toc import PaginatedSoupTemplate
from .soup.searchable import SearchableSoupTemplate


class NovelFullTemplate(SearchableSoupTemplate, PaginatedSoupTemplate):
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

    def parse_title(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one("h3.title")
        if not isinstance(tag, Tag):
            raise LNException("No title found")
        self.novel_title = tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one(".book img")
        if not isinstance(tag, Tag):
            return
        if tag.has_attr("data-src"):
            self.novel_cover = self.absolute_url(tag["data-src"])
        elif tag.has_attr("src"):
            self.novel_cover = self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup) -> None:
        self.novel_author = ", ".join(
            [
                a.text.strip()
                for a in soup.select(
                    ".info a[href*='/au/'],"
                    + ".info a[href*='/authors/'],"
                    + ".info a[href*='/author/'],"
                    + ".info a[href*='/a/']"
                )
            ]
        )

    def generate_page_soups(
        self, soup: BeautifulSoup
    ) -> Generator[BeautifulSoup, None, None]:
        nl_id_tag = soup.select_one("#rating[data-novel-id]")
        if not isinstance(nl_id_tag, Tag):
            raise LNException("No novel_id found")

        nl_id = nl_id_tag["data-novel-id"]
        script = soup.find("script", text=re.compile(r"ajaxChapterOptionUrl\s+="))
        if isinstance(script, Tag):
            url = f"{self.home_url}ajax-chapter-option?novelId={nl_id}"
        else:
            url = f"{self.home_url}ajax/chapter-archive?novelId={nl_id}"

        return self.get_soup(url)

    def select_chapter_tags(self, soup: BeautifulSoup) -> Iterable[Tag]:
        return soup.select("ul.list-chapter > li > a, select > option")

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(
                tag["href"] if tag.has_attr("href") else tag["value"]
            ),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        body = soup.select_one("#chr-content, #chapter-content")
        for img in body.select("img"):
            if img.has_attr("data-src"):
                img.attrs = {"src": img["data-src"]}
        self.cleaner.clean_contents(body)
        return body
