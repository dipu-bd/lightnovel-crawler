# -*- coding: utf-8 -*-
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, Volume
from lncrawl.templates.wordpress import WordpressTemplate


class LibraryNovel(WordpressTemplate):
    base_url = "https://librarynovel.com/"
    chapter_body_selector = ".text-left"
    novel_author_selector = '.author-content a[href*="novel-author"]'

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        chapter_list_url = self.absolute_url("ajax/chapters", novel.url)
        ch_soup = self.scraper.post_soup(chapter_list_url, headers={"accept": "*/*"})
        tags = []
        for a in reversed(ch_soup.select('.wp-manga-chapter a[href*="/novel"]')):
            for span in a.find_all("span"):
                span.extract()
            tags.append(a)
        return tags
