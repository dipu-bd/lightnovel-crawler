# -*- coding: utf-8 -*-
from lncrawl.core import BrowserTemplate, Novel, PageSoup


class LNTCrawler(BrowserTemplate):
    base_url = ["https://lightnovelstranslations.com/"]

    has_manga = False
    has_mtl = False

    chapter_title_selector = ".novel_title"
    novel_cover_selector = ".novel-image img"
    novel_author_selector = ".entry-content > p"
    chapter_list_selector = ".novel_list_chapter_content li.unlock a"
    chapter_body_selector = ".text_story"

    def build_novel_url(self, novel: Novel) -> str:
        return f"{self.scraper.origin}{novel.url}/?tab=table_contents"

    def parse_author(self, soup: PageSoup, novel: Novel) -> None:
        authors = []
        for p in soup.select(self.novel_author_selector):
            if "Author" in p.text:
                authors.append(p.text.replace("Author:", "").strip())
        novel.author = ", ".join(authors)
