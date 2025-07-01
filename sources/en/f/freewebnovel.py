# -*- coding: utf-8 -*-
import re
import unicodedata

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate


class FreeWebNovelCrawler(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    base_url = [
        "https://freewebnovel.com/",
        "https://bednovel.com/",
        "https://innread.com/",
        "https://innnovel.com/",
        "https://libread.com/",
        "https://libread.org/",
    ]

    def initialize(self) -> None:
        self.init_executor(ratelimit=2)
        self.cleaner.bad_tags.update(["h4", "sub"])
        self.cleaner.bad_tag_text_pairs.update(
            {
                "p": [
                    r"freewebnovel\.com",
                    r"innread\.com",
                    r"bednovel\.com",
                    r"Updates by Freewebnovel\. com",
                    r"” Search Freewebnovel\.com\. on google”\.",
                    r"\/ Please Keep reading on MYFreeWebNovel\.C0M",
                    r"please keep reading on Freewebnovel\(dot\)C0M",
                    r"Continue\_reading on Freewebnovel\.com",
                    r"Continue \-reading on Freewebnovel\.com",
                    r"\/ Please Keep reading 0n FreewebNOVEL\.C0M",
                    r"\[ Follow current novels on Freewebnovel\.com \]",
                    r"‘Freewebnovel\.com\*’",
                    r"‘Search Freewebnovel\.com\, on google’",
                    r"‘ Search Freewebnovel\.com\(\) ‘",
                    r"“Freewebnovel\.com \.”",
                    r"“Please reading on Freewebnovel\.com\.”",
                    r"“Search Freewebnovel\.com\. on google”",
                    r"“Read more on Freewebnovel\.com\. org”",
                    r"Thank you for reading on FreeWebNovel\.me",
                    r"Please reading \-on Freewebnovel\.com",
                    r"”Search \(Freewebnovel\.com\(\) on google\”\?",
                    r"“Please reading on Freewebnovel\.com \:”",
                    r"”Please reading on Freewebnovel\.com\.”\?",
                    r"“Please reading on Freewebnovel\.com\&gt\; ”",
                ],
                "i": [r"\[ Follow current novels on Freewebnovel\.com \]"],
            }
        )

    def select_search_items(self, query: str):
        data = {"searchkey": query}
        soup = self.post_soup(f"{self.home_url}search/", data=data)
        yield from soup.select(".col-content .con .txt h3 a")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        return SearchResult(
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".m-desc h1.tit")
        assert isinstance(tag, Tag)
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".m-imgtxt img")
        assert isinstance(tag, Tag)
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup):
        for a in soup.select(".m-imgtxt a[href*='/authors/']"):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup):
        chapters = soup.select("#idData")
        for chapter in chapters:
            yield from chapter.select("li > a")

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            url=self.absolute_url(tag["href"]),
            title=tag.text.strip(),
        )

    def normalize_text(self, text: str) -> str:
        return unicodedata.normalize("NFKC", text)

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        body_tag = soup.select_one(".m-read")
        # style element on page that hides usually last paragraph which contains randomised self-promo text
        has_promo = soup.find("style", text=re.compile("p:nth-last-child\\(\\d\\)"))
        if body_tag:
            normalized_body = self.normalize_text(str(body_tag))
            normalized_soup = BeautifulSoup(normalized_body, "html.parser")
            if has_promo:
                selectors = []
                style_content = has_promo.get_text(strip=True)
                rules = re.findall(r"([^{]+)\{[^}]*\}", style_content)
                for rule in rules:
                    selectors.extend(
                        selector
                        for selector in rule.split(",")
                        if not re.search(r"p:nth-last-child\(\d+\)", selector.strip())
                    )
                selectors = list(filter(None, set(selectors)))

                for promo_selector in selectors:
                    random_self_promo = normalized_soup.select(promo_selector)
                    [tag.decompose() for tag in random_self_promo]
            return normalized_soup.select_one(".txt")
        return body_tag.select_one(".txt")
