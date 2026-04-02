# -*- coding: utf-8 -*-
from lncrawl.core import Novel, PageSoup
from lncrawl.templates.wordpress import WordpressTemplate


class MeowNovel(WordpressTemplate):
    base_url = "https://meownovel.com/"
    chapter_body_selector = "div.text-left"
    novel_author_selector = '.author-content a[href*="novel-author"]'
    madara_search_quote_mode = "quote"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                "a",
                ".google-auto-placed",
                ".ap_container",
            ]
        )
        self.cleaner.bad_text_regex.update(
            [
                "Read First at meownovel.com",
                "Latest Update on meow novel.com",
                "me ow no vel.com is releasing your favorite novel",
                "You can read this novel at m eow no vel.com for better experience",
                "meow novel . com will be your favorite novel site",
                "Read only at m e o w n o v e l . c o m",
            ]
        )

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:title"]')
        novel.title = tag["content"].rsplit(" | ", 1)[0].strip()

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:image"]')
        if tag and tag.get("content"):
            novel.cover_url = self.absolute_url(tag["content"])
        else:
            super().parse_cover(soup, novel)
