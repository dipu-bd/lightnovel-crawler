# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate

logger = logging.getLogger(__name__)


class LoreNovelsCrawler(SoupTemplate):
    base_url = "https://lorenovels.com/"

    novel_cover_selector = "main .entry-content .wp-block-group .wp-block-image img"
    novel_title_selector = "div.is-vertical:nth-child(1) > h2:nth-child(2)"
    novel_author_selector = "div.is-vertical:nth-child(2) > h2:nth-child(2)"
    novel_tags_selector = "div.wp-block-group:nth-child(3) > h2:nth-child(2)" # remember to split via ", "
    novel_synopsis_selector = ".wp-container-core-group-is-layout-7faab66b > p.wp-block-paragraph"
    
    chapter_list_reverse = True
    chapter_list_selector = ".wp-block-latest-posts__list li"
    chapter_url_selector = "a"

    chapter_body_selector = "main .entry-content"

    
    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:

        for tag in soup.select(self.novel_tags_selector):
            if ", " in tag.text:
                multi_tag_subtags = tag.text.split(", ")
                for individual_tag in multi_tag_subtags:
                    novel.tags.append(individual_tag)
        
        if not novel.tags:
           meta_tag = soup.select_one(SoupTemplate.novel_tags_selector)
           novel.tags = [t.strip() for t in meta_tag.get("content").split(",")]
    
    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(self.novel_synopsis_selector)
        novel.synopsis = self.cleaner.extract_contents(tag)
        if not novel.synopsis:
            meta_tag = soup.select_one(SoupTemplate.novel_synopsis_selector)
            content = PageSoup.create(meta_tag.get("content"))
            novel.synopsis = self.cleaner.extract_contents(content)
    
