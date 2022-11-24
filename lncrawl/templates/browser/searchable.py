from abc import abstractmethod
from typing import Generator, List

from bs4 import Tag

from ...core.exeptions import FallbackToBrowser
from ...models import SearchResult
from ..soup.searchable import SearchableSoupTemplate
from .general import GeneralBrowserTemplate


class SearchableBrowserTemplate(GeneralBrowserTemplate, SearchableSoupTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def search_novel_in_scraper(self, query: str) -> List[SearchResult]:
        tags = self.select_search_items(query)
        return list(self.process_search_results(tags))

    def search_novel_in_browser(self, query: str) -> List[SearchResult]:
        tags = self.select_search_items_in_browser(query)
        return list(self.process_search_results_in_browser(tags))

    def process_search_results_in_browser(
        self, tags: Generator[Tag, None, None]
    ) -> Generator[Tag, None, None]:
        """Process novel item tag and generates search results from the browser"""
        count = 0
        for tag in tags:
            if not isinstance(tag, Tag):
                continue
            count += 1
            if count == 10:
                break
            yield self.parse_search_item_in_browser(tag)

    @abstractmethod
    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        raise FallbackToBrowser()

    @abstractmethod
    def select_search_items_in_browser(self, query: str) -> Generator[Tag, None, None]:
        """Select novel items found by the query using the browser"""
        raise NotImplementedError()

    def parse_search_item_in_browser(self, tag: Tag) -> SearchResult:
        """Parse a tag and return single search result"""
        return self.parse_search_item(tag)
