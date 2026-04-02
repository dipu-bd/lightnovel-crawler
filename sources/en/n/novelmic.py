# -*- coding: utf-8 -*-
from lncrawl.core import Novel, PageSoup
from lncrawl.templates.wordpress import WordpressMangaTemplate


class NovelMic(WordpressMangaTemplate):
    base_url = "https://novelmic.com/"

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:title"]')
        novel.title = tag["content"].rsplit(" ", 1)[0].strip()

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:image"]')
        if tag and tag.get("content"):
            novel.cover_url = self.absolute_url(tag["content"])
        else:
            super().parse_cover(soup, novel)
