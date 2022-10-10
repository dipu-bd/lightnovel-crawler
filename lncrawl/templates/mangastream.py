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
            info=info.text.strip() if info else "",
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one("h1.entry-title")

        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".thumbook img.wp-post-image")
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])

        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup):
        for a in soup.select(".spe a[href*='/writer/']"):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup):
        chapters = soup.select(".eplister li > a")
        first_li = soup.select_one(".eplister li")
        if "tseplsfrst" not in first_li.get("class", ""):
            chapters = reversed(chapters)

        yield from chapters

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.select_one(".epl-title").text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".entry-content")
