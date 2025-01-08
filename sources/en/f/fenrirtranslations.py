# -*- coding: utf-8 -*-
import logging

from bs4 import BeautifulSoup

from lncrawl.templates.madara import MadaraTemplate
logger = logging.getLogger(__name__)


class FenrirTranslationsCrawler(MadaraTemplate):
    base_url = ["https://fenrirtranslations.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                "div.chapter-warning",
                "div.code-block"
            ]
        )

    def parse_authors(self, soup: BeautifulSoup):
        for a in soup.select('.manga-authors a[href*="author"]'):
            yield a.text.strip()

    def parse_summary(self, soup):
        possible_summary = soup.select_one(".manga-summary")
        return self.cleaner.extract_contents(possible_summary)

    def select_chapter_tags(self, soup: BeautifulSoup):
        try:
            clean_novel_url = self.novel_url.split("?")[0].strip("/")
            response = self.submit_form(f"{clean_novel_url}/ajax/chapters/")
            soup = self.make_soup(response)
            chapters = soup.select(".free ul.main .wp-manga-chapter a")
            yield from reversed(chapters)
        except Exception as e:
            logger.debug("Failed to fetch chapters using ajax", e)
