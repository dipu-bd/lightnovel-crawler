from urllib.parse import urlencode

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate


class MangaStreamTemplate(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    is_template = True

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])

    def select_search_items(self, query: str):
        params = dict(s=query)
        soup = self.get_soup(f"{self.home_url}?{urlencode(params)}")

        yield from soup.select(".listupd > article")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        a = tag.select_one("a.tip")
        title = tag.select_one("span.ntitle")
        info = tag.select_one("span.nchapter")

        return SearchResult(
            title=title.text.strip() if title else a.text.strip(),
            url=self.absolute_url(a["href"]),
            info=info.text.strip() if isinstance(info, Tag) else "",
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one("h1.entry-title")

        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".thumbook img, meta[property='og:image']")
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])

        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

        if tag.has_attr("content"):
            return self.absolute_url(tag["content"])

    def parse_authors(self, soup: BeautifulSoup):
        for a in soup.select(".spe a[href*='/writer/']"):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup):
        chapters = soup.select(".eplister li > a, .eplister li .eph-num > a")
        first_li = soup.select_one(".eplister li")
        if "tseplsfrst" not in first_li.get("class", "") or 1 == first_li.get(
            "data-num", 0
        ):
            chapters = reversed(chapters)

        yield from chapters

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        title = tag.select_one(".epl-title")
        return Chapter(
            id=id,
            title=title.text.strip()
            if isinstance(title, Tag)
            else tag.select_one("span").text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one("#readernovel, #readerarea, .entry-content")
