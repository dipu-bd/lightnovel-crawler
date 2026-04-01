# -*- coding: utf-8 -*-
import logging
import re
from typing import Generator, Union

from lncrawl.core import Chapter, PageSoup, SearchResult, Volume
from lncrawl.templates.soup.searchable import SearchableSoupTemplate

logger = logging.getLogger(__name__)
search_url = "https://cheldra.wordpress.com"


class Cheldra(SearchableSoupTemplate):
    base_url = ["https://cheldra.wordpress.com"]

    def initialize(self) -> None:
        # You can customize `TextCleaner` and other necessary things.
        pass

    def select_search_items(self, query: str) -> Generator[PageSoup, None, None]:
        soup = self.post_soup(self.home_url)
        results = soup.select(".site-header .site-header-top .main-navigation div ul li")
        filtered_results = [
            result
            for result in results
            if query in str(result.find("a", href=True)) and result.find("a", href=True).text != "About"
        ]
        yield from filtered_results
        pass

    def parse_search_item(self, tag: PageSoup) -> SearchResult:
        url = tag.find("a")["href"]
        soup = self.post_soup(url)
        title = soup.select_one(".entry-title").text.strip()
        return SearchResult(title=title, url=url)

    def get_novel_soup(self) -> PageSoup:
        links = self.get_soup(self.novel_url).select("div.entry-content p:not([class]) a")
        seven_seas_url = next(link["href"] for link in links if link.text == "Seven Seas")
        seven_seas_soup = self.post_soup(seven_seas_url)
        self.seven_seas_soup = seven_seas_soup
        return self.get_soup(self.novel_url)

    def parse_title(self, soup: PageSoup) -> str:
        # The soup here is the result of `self.get_soup(self.novel_url)`
        return soup.select_one(".entry-title").text

    def parse_cover(self, soup: PageSoup) -> str:
        return self.seven_seas_soup.select_one("div.volumes-container a img")["src"]

    def parse_author(self, soup):
        # renvoyer une liste de chaînes plutôt qu'un générateur
        txt = soup.select_one("div.entry-content p:not([class])").text
        # Eviter lstrip("Author: ") qui enlève un ensemble de caractères :
        author = re.sub(r"^Author:\s*", "", txt)
        return [author]

    def parse_tags(self, soup):
        soup = self.seven_seas_soup
        meta = soup.select_one("div.info div#series-meta")
        genre_tags = meta.find("b", string="Genre(s):")
        genres = []
        if genre_tags.tag:
            for tag in genre_tags.tag.find_next_siblings():
                if tag.name == "a":
                    genres.append(tag.text.strip())
                else:
                    break
        return genres

    def parse_summary(self, soup):
        # description unique -> string
        soup = self.seven_seas_soup
        return soup.select_one("div.series-description div.entry p").text

    def parse_chapter_list(self, soup: PageSoup) -> Generator[Union[Chapter, Volume], None, None]:
        # The soup here is the result of `self.get_soup(self.novel_url)`
        chap_list = soup.select("div.entry-content p.has-text-align-justify.has-small-font-size a")
        seen_vol_ids = set()
        seen_chap_id = set()
        for i, chap in enumerate(chap_list):
            chap_title = chap.text
            if i + 1 < len(chap_list) and chap_list[i + 1]["href"] == chap["href"]:
                chap_title = chap_list[i + 1].text
            elif chap_list[i - 1]["href"] == chap["href"]:
                continue
            if "–" in chap.text:
                separated_title = chap.text.split("–")
            else:
                separated_title = chap.text.split("-")
            try:
                chap_id = int(separated_title[0].strip())
                vol_id = 1 + chap_id // 100
            except ValueError:
                continue
            chap_url = chap["href"]
            if chap_id not in seen_chap_id:
                seen_chap_id.add(chap_id)
                yield Chapter(title=chap_title, id=chap_id, url=chap_url, volume=vol_id)
            if vol_id not in seen_vol_ids:
                seen_vol_ids.add(vol_id)
                yield Volume(
                    id=vol_id,
                )
        pass

    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        # The soup here is the result of `self.get_soup(chapter.url)`
        return soup.select_one("div#content #primary #main article div.entry-content")
