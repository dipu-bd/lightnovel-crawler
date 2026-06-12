# -*- coding: utf-8 -*-
import logging
import re

from typing import Iterable, Optional
from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume, Browser

logger = logging.getLogger(__name__)


class DreamyTranslationsCrawler(SoupTemplate):
    base_url = ["https://dreamy-translations.com/"]

    novel_title_selector = ".text-2xl"
    novel_author_selector = ".mt-1 > span:nth-child(1)"
    novel_cover_selector = ".object-cover"
    novel_tags_selector = "div.flex-wrap:nth-child(2) span, div.flex-wrap:nth-child(3) span"

    novel_toc_selector = "#tocItems"
    novel_synopsis_selector = "div.min-h-0:nth-child(5) > div:nth-child(1)"

    chapter_list_selector = ".space-y-0\.5 a"
    chapter_title_selector = "a.group > div:nth-child(1) > p"

    chapter_body_selector = "main article div"
    chapter_elem_selector = ".paragraph .line"

    auto_create_volumes = False

    def initialize(self) -> None:
        self.taskman.init_executor(workers=2) 
        # The browser doesn't handle concurrency very well, likely due to networking limitations

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        """Parse and set the novel categories/genres/tags"""
        #novel.tags = [tag.text for tag in soup.select(self.novel_tags_selector)]
        for tag in soup.select(self.novel_tags_selector):
            tag_text = tag.text
            if "#" in tag_text:
                tag_text = tag_text.strip("#") # Remove octothorpe from tags if applicable
            novel.tags.append(tag_text)

    def parse_chapter_item(self, soup: PageSoup, chapter_id: int) -> Chapter:
        chapter = Chapter(id=chapter_id)
        self.parse_chapter_title(soup, chapter)
        self.parse_chapter_url(soup, chapter)
        return chapter

    def parse_chapter_title(self, soup: PageSoup, chapter: Chapter) -> None:
        """Parse and set the chapter title"""
        title_tag = soup.select_one(self.chapter_title_selector) or soup
        #print("Chapter title tag: " + str(title_tag))
        print("Chapter title: " + title_tag.text)
        chapter.title = title_tag.text

    def select_chapter_tags(
        self, soup: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        chapters = list(soup.select(self.chapter_list_selector))

        for a in chapters:
            yield a

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.get_chapter_soup(chapter, True)
        body = soup.select_one(self.chapter_body_selector)
        self.parse_chapter_body(body, chapter)
    
    # This site is JS-heavy, so the only way I found it working is to use the browser
    def get_novel_soup(self, novel: Novel, extra_timeout=False) -> PageSoup:
        url = self.build_novel_url(novel)
        with self.create_browser() as browser:
            browser.visit(novel.url)
            browser.wait("#loadingMask", inverse=True, timeout=5)
            if extra_timeout: # For JS-heavy pages, call with extra_timeout=True
                import time
                time.sleep(2)
            
            soup = browser.soup
            return soup

    def get_chapter_soup(self, chapter: Chapter, extra_timeout=False) -> PageSoup:
        url = self.build_chapter_url(chapter)
        with self.create_browser() as browser:
            browser.visit(chapter.url)
            browser.wait("#loadingMask", inverse=True, timeout=2)
            browser.wait(self.chapter_body_selector)
            if extra_timeout:
                import time
                time.sleep(2)
            soup = browser.soup
            return soup