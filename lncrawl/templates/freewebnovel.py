# -*- coding: utf-8 -*-
import re
import unicodedata
from typing import Any, Iterable, List

from lncrawl.core import BrowserTemplate, Chapter, PageSoup


class FreewebnovelTemplate(BrowserTemplate):
    is_template = True

    search_item_list_selector = ".col-content .con .txt h3 a"
    novel_title_selector = ".m-desc h1.tit"
    novel_cover_selector = ".m-imgtxt img"
    novel_author_selector = ".m-imgtxt a[href*='/authors/']"
    chapter_list_selector = "#idData li > a"
    chapter_body_selector = ".m-read"

    def initialize(self) -> None:
        self.taskman.init_executor(workers=2)
        self.cleaner.bad_tags.update(["h4", "sub"])
        self.cleaner.bad_text_regex.update(
            [
                r"Updates by Freewebnovel\. com",
                r"” Search Freewebnovel\.com\. on google”\.",
                r"[\w\s]+[fF]ree\s?[Ww]eb\s?[nN]ovel[.\s]?([cC][oO0][mM])?",
            ]
        )

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        soup = self.scraper.post_soup(
            f"{self.scraper.origin}search/",
            {"searchkey": query},
        )
        return soup.select(".col-content .con .txt h3 a")

    def normalize_text(self, text: str) -> str:
        return unicodedata.normalize("NFKC", text)

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.scraper.get_soup(chapter.url)

        # style element on page that hides usually last paragraph which contains randomised self-promo text
        has_promo = soup.find("style", text=re.compile("p:nth-last-child\\(\\d\\)"))
        style_content = has_promo.get_text(strip=True)
        rules = re.findall(r"([^{]+)\{[^}]*\}", style_content)

        selectors: List[Any] = []
        for rule in rules:
            selectors.extend(
                selector
                for selector in rule.split(",")
                if not re.search(r"p:nth-last-child\(\d+\)", selector.strip())
            )
        selectors = list(filter(None, set(selectors)))

        body_tag = soup.select_one(self.chapter_body_selector)
        normalized_body = self.normalize_text(body_tag.outer_html)
        normalized_soup = PageSoup.create(normalized_body, parser="html.parser")
        for promo_selector in selectors:
            normalized_soup.decompose(promo_selector)

        contents = normalized_soup.select_one(".txt") or normalized_soup
        chapter.body = self.cleaner.extract_contents(contents)
