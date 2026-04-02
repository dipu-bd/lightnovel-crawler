# -*- coding: utf-8 -*-
from lncrawl.core import Novel, PageSoup
from lncrawl.templates.wordpress import WordpressTemplate


class OMGNovelsCrawler(WordpressTemplate):
    base_url = "https://omgnovels.com/"
    chapter_body_selector = "div.text-left"

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:image"]')
        if tag and tag.get("content"):
            novel.cover_url = self.absolute_url(tag["content"])
        else:
            super().parse_cover(soup, novel)
