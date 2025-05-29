# -*- coding: utf-8 -*-

from typing import Generator
from bs4 import BeautifulSoup, Tag
from lncrawl.templates.novelpub import NovelPubTemplate


class PandaNovelCo(NovelPubTemplate):
    base_url = [
        "https://pandanovel.co/",
    ]

    # We override because we do not have a request token like other novel pub
    # (without that wrong error is raised and browser search isn't triggered)
    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        self.submit_form(
            f"{self.home_url}lnsearchlive",
            data={"inputContent": query},
            headers={
                "referer": f"{self.home_url}search",
            },
        )

    # override this because somehow novel_url is always missing trailing /
    def select_chapter_tags_in_browser(self):
        next_link = f"{self.novel_url}/chapters"
        while next_link:
            self.browser.visit(next_link)
            self.browser.wait("ul.chapter-list li")
            chapter_list = self.browser.find("ul.chapter-list")
            yield from chapter_list.as_tag().select("li a")
            try:
                next_link = self.browser.find('.PagedList-skipToNext a[rel="next"]')
                next_link = next_link.get_attribute("href")
            except Exception:
                next_link = False

    # .chapter-content -> #content
    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        self.browser.wait("#content")
        return soup.select_one("#content")
