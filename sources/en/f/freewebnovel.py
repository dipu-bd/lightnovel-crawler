# -*- coding: utf-8 -*-
import re
import unicodedata
from typing import Any, List

from lncrawl.core import Chapter, PageSoup, SearchResult
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

    def parse_search_item(self, tag: PageSoup) -> SearchResult:
        return SearchResult(
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def parse_title(self, soup: PageSoup) -> str:
        tag = soup.select_one(".m-desc h1.tit")
        return tag.text.strip()

    def parse_cover(self, soup: PageSoup) -> str:
        tag = soup.select_one(".m-imgtxt img")
        if tag.has_attr("data-src"):
            return self.absolute_url(tag["data-src"])
        if tag.has_attr("src"):
            return self.absolute_url(tag["src"])
        return ""

    def parse_authors(self, soup: PageSoup):
        for a in soup.select(".m-imgtxt a[href*='/authors/']"):
            yield a.text.strip()

    def select_chapter_tags(self, soup: PageSoup):
        chapters = soup.select("#idData")
        for chapter in chapters:
            yield from chapter.select("li > a")

    def parse_chapter_item(self, tag: PageSoup, id: int) -> Chapter:
        return Chapter(
            id=id,
            url=self.absolute_url(tag["href"]),
            title=tag.text.strip(),
        )

    def normalize_text(self, text: str) -> str:
        return unicodedata.normalize("NFKC", text)

    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        body_tag = soup.select_one(".m-read")
        if not body_tag:
            return None

        # style element on page that hides usually last paragraph which contains randomised self-promo text
        has_promo = soup.find("style", text=re.compile("p:nth-last-child\\(\\d\\)"))
        if not has_promo:
            return None

        selectors: List[Any] = []
        style_content = has_promo.get_text(strip=True)
        rules = re.findall(r"([^{]+)\{[^}]*\}", style_content)
        for rule in rules:
            selectors.extend(
                selector for selector in rule.split(",") if not re.search(r"p:nth-last-child\(\d+\)", selector.strip())
            )
        selectors = list(filter(None, set(selectors)))

        normalized_body = self.normalize_text(str(body_tag))
        normalized_soup = PageSoup.create(normalized_body, parser="html.parser")
        for promo_selector in selectors:
            random_self_promo = normalized_soup.select(promo_selector)
            for tag in random_self_promo:
                tag.decompose()
        return normalized_soup.select_one(".txt")
