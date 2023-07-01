from urllib.parse import urlencode

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult, Volume
from lncrawl.templates.browser.optional_volume import OptionalVolumeBrowserTemplate
from lncrawl.templates.browser.searchable import SearchableBrowserTemplate


class MangaStreamTemplate(SearchableBrowserTemplate, OptionalVolumeBrowserTemplate):
    is_template = True

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])

    def select_search_items(self, query: str):
        params = dict(s=query)
        soup = self.get_soup(f"{self.home_url}?{urlencode(params)}")
        yield from soup.select(".listupd > article")

    def select_search_items_in_browser(self, query: str):
        params = dict(s=query)
        self.visit(f"{self.home_url}?{urlencode(params)}")
        yield from self.browser.soup.select(".listupd > article")

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
        title = soup.select_one("h1.entry-title")
        assert title
        return title.text.strip()

    def parse_title_in_browser(self) -> str:
        self.browser.wait("h1.entry-title")
        return self.parse_title(self.browser.soup)

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(
            ".thumbook img, meta[property='og:image'],.sertothumb img"
        )
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])

        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

        if tag.has_attr("content"):
            return self.absolute_url(tag["content"])

    def parse_authors(self, soup: BeautifulSoup):
        for a in soup.select(".spe a[href*='/writer/']"):
            yield a.text.strip()

    def select_volume_tags(self, soup: BeautifulSoup):
        return []

    def parse_volume_item(self, tag: Tag, id: int) -> Volume:
        return Volume(id=id)

    def select_chapter_tags(self, tag: Tag):
        chapters = tag.select(".eplister li a")
        first_li = tag.select_one(".eplister li")
        li_class = first_li.get("class", "") if first_li else ""
        if first_li.get("data-num", 0) == 1 or "tseplsfrst" not in li_class:
            yield from reversed(chapters)
        else:
            yield from chapters

    def parse_chapter_item(self, tag: Tag, id: int, vol: Volume) -> Chapter:
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

    def visit_chapter_page_in_browser(self, chapter: Chapter) -> None:
        self.visit(chapter.url)
        self.browser.wait("#readernovel, #readerarea, .entry-content,.mainholder")
