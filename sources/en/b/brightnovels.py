# -*- coding: utf-8 -*-
import logging
import re

from typing import Iterable, Optional
from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume, Browser

logger = logging.getLogger(__name__)


class BrightNovelsCrawler(SoupTemplate):
    base_url = ["https://brightnovels.com/"]

    novel_title_selector = ".text-2xl"
    novel_author_selector = "div.text-muted-foreground:nth-child(3)"
    novel_cover_selector = ".w-48 > img:nth-child(1)"
    novel_tags_selector = "div.flex:nth-child(4)"

    novel_toc_selector = "section.container:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)"
    novel_toc_free_chap_selector = ".space-y-4 > div:nth-child(1) > div:nth-child(1) > button:nth-child(2)" # select free chapters
    novel_toc_prem_chap_icon_selector = "a.relative:nth-child(1) > div:nth-child(1) > div:nth-child(2) > svg.lucide-lock-icon"
    novel_synopsis_selector = ".prose"

    chapter_list_reverse = True
    chapter_list_selector = "section.container:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) .grid a"
    chapter_title_selector = ".flex .text-sm"

    chapter_body_selector = "#app > div > main > div > div > div.rounded-lg.border.bg-card.text-card-foreground.shadow-xs.relative.mb-10.overflow-hidden.p-6.md\:p-8 > div > div"

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
        
        for a in reversed(chapters):
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
            browser.click(self.novel_toc_free_chap_selector)
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
            browser.wait(self.chapter_body_selector)
            if extra_timeout:
                import time
                time.sleep(2)
            soup = browser.soup
            return soup