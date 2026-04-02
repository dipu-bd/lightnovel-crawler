# -*- coding: utf-8 -*-
from lncrawl.core import Novel, PageSoup
from lncrawl.templates.wordpress import WordpressTemplate


class NeoSekaiCrawler(WordpressTemplate):
    base_url = "https://www.neosekaitranslations.com/"
    novel_author_selector = '.author-content a[href*="novel-author"]'

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:title"]')
        novel.title = tag["content"].rsplit(" ", 1)[0].strip()
