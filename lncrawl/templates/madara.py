from typing import Iterable
from urllib.parse import urlencode

from bs4 import BeautifulSoup, Tag

from ..core.exeptions import LNException
from ..models import Chapter, SearchResult
from .soup.searchable import SearchableSoupTemplate
from .soup.single_page import SinglePageSoupTemplate


class MadaraTemplate(SearchableSoupTemplate, SinglePageSoupTemplate):
    is_template = True

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
        self.cleaner.bad_css.update(['a[href="javascript:void(0)"]'])

    def get_search_page_soup(self, query: str) -> BeautifulSoup:
        params = dict(
            s=query,
            post_type="wp-manga",
            op="",
            author="",
            artist="",
            release="",
            adult="",
        )
        return self.get_soup(f"{self.home_url}?{urlencode(params)}")

    def select_search_items(self, soup: BeautifulSoup) -> Iterable[Tag]:
        return soup.select(".c-tabs-item__content")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        a = tag.select_one(".post-title h3 a")
        latest = tag.select_one(".latest-chap .chapter a").text
        votes = tag.select_one(".rating .total_votes").text
        return SearchResult(
            title=a.text.strip(),
            url=self.absolute_url(a["href"]),
            info="%s | Rating: %s" % (latest, votes),
        )

    def parse_title(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one(".post-title h1")
        if not isinstance(tag, Tag):
            raise LNException("No title found")
        for span in tag.select("span"):
            span.extract()
        self.novel_title = tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one(".summary_image a img")
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
                for a in soup.select('.author-content a[href*="manga-author"]')
            ]
        )

    def select_chapter_tags(self, soup: BeautifulSoup) -> Iterable[Tag]:
        nl_id = soup.select_one('[id^="manga-chapters-holder"][data-id]')
        if isinstance(nl_id, Tag):
            response = self.submit_form(
                f"{self.home_url}wp-admin/admin-ajax.php",
                data={
                    "action": "manga_get_chapters",
                    "manga": nl_id["data-id"],
                },
            )
        else:
            clean_novel_url = self.novel_url.split("?")[0].strip("/")
            response = self.submit_form(f"{clean_novel_url}/ajax/chapters/")

        soup = self.make_soup(response)
        return reversed(soup.select("ul.main .wp-manga-chapter > a"))

    def parse_chapter_item(self, a: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=a.text.strip(),
            url=self.absolute_url(a["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        body = soup.select_one("div.reading-content")
        for img in body.select("img"):
            if img.has_attr("data-src"):
                img.attrs = {"src": img["data-src"]}
        return body
