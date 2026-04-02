# -*- coding: utf-8 -*-
from lncrawl.core import Chapter, Novel, PageSoup
from lncrawl.templates.wordpress import WordpressTemplate


class WoopReadCrawler(WordpressTemplate):
    base_url = "https://woopread.com/"

    def initialize(self) -> None:
        self.regex_novel_id = r'"manga_id"\s*:\s*"(?P<id>\d+)"'

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(".post-title h1")
        novel.title = tag.text.strip() if tag else ""

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        ac = soup.select_one(".author-content")
        novel.author = ac.text.strip() if ac else ""

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:image"]')
        if tag and tag.get("content"):
            novel.cover_url = self.absolute_url(tag["content"])
        else:
            super().parse_cover(soup, novel)

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.scraper.get_soup(self.build_chapter_url(chapter))
        if "This chapter is locked!" in soup.text:
            chapter.body = ""
            return
        contents = soup.select_one(".container .reading-content div")
        if not contents:
            chapter.body = ""
            return
        for content in contents.select("p"):
            for bad in ("Translator:", "Editor:"):
                if bad in content.text:
                    content.extract()
                    break
        chapter.body = self.cleaner.extract_contents(contents)
