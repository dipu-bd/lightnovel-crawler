import re
from urllib.parse import urlencode

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult, Volume
from lncrawl.templates.browser.optional_volume import OptionalVolumeBrowserTemplate
from lncrawl.templates.browser.searchable import SearchableBrowserTemplate

digit_regex = re.compile(r"page[-,=](\d+)")


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
        title = soup.select_one("h1.entry-title,h2.text-2xl")
        assert title
        return title.text.strip()

    def visit_novel_page_in_browser(self) -> BeautifulSoup:
        self.visit(self.novel_url)
        self.browser.wait("h1.entry-title, .container")

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(
            ".thumbook img, meta[property='og:image'],.sertothumb img,img.h-full"
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
        if tag.select(".eplister"):
            chapters = tag.select(".eplister li a")
            first_li = tag.select_one(".eplister li")
            li_class = first_li.get("class", "") if first_li else ""
            if first_li.get("data-num", 0) == 1 or "tseplsfrst" not in li_class:
                yield from reversed(chapters)
            else:
                yield from chapters
        if tag.select("li.pagination-link"):
            page_count = max(
                [
                    int(digit_regex.search(li.get("onclick")).group(1))
                    for li in tag.select("li.pagination-link", onclick=True)
                    if li.get("onclick")
                ]
            )

            if not page_count:
                page_count = 1

            futures = [self.executor.submit(lambda x: x, tag)]
            futures += [
                self.executor.submit(self.get_soup, f"{self.novel_url}?page={p}")
                for p in range(2, page_count + 1)
            ]
            self.resolve_futures(futures, desc="TOC", unit="page")

            for f in reversed(futures):
                soup = f.result()
                yield from reversed(soup.select("#chapters-list a"))

    def select_chapter_tags_in_browser(self, tag: Tag):
        if self.browser.soup.select(".eplister"):
            yield from self.select_chapter_tags(self.browser.soup)
        if self.browser.soup.select("li.pagination-link"):
            page_count = max(
                [
                    int(digit_regex.search(li.get("onclick")).group(1))
                    for li in self.browser.soup.select(
                        "li.pagination-link", onclick=True
                    )
                    if li.get("onclick")
                ]
            )
            if not page_count:
                page_count = 1
            futures_pages = [self.browser.soup]
            for p in range(2, page_count + 1):
                self.browser.visit(f"{self.novel_url}?page={p}")
                self.browser.wait("h1.entry-title, .container")
                futures_pages += [self.browser.soup]

            for f in reversed(futures_pages):
                yield from reversed(f.select("#chapters-list a"))

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
        return soup.select_one(
            "#readernovel, #readerarea, .entry-content,.chap-content"
        )

    def visit_chapter_page_in_browser(self, chapter: Chapter) -> None:
        self.visit(chapter.url)
        self.browser.wait(
            "#readernovel, #readerarea, .entry-content,.mainholder,.chap-content"
        )
