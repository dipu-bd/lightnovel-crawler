# -*- coding: utf-8 -*-
from lncrawl.core import Novel, PageSoup
from lncrawl.templates.wordpress import WordpressTemplate


class LatestNovelCrawler(WordpressTemplate):
    base_url = "https://latestnovel.net/"
    chapter_body_selector = ".reading-content .text-left"
    novel_author_selector = '.author-content a[href*="novel-author"]'

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            ["You can read the novel online free at LatestNovel.Net or NovelZone.Net"]
        )

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:title"]')
        novel.title = tag["content"].rsplit(" ", 1)[0].strip()
