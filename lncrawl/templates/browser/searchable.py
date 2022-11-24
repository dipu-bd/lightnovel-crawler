from abc import abstractmethod
from typing import Generator, List

from bs4 import Tag

from ...core.exeptions import FallbackToBrowser
from ...models import SearchResult
from ..soup.searchable import SearchableSoupTemplate
from .general import GeneralBrowserTemplate


class SearchableBrowserTemplate(GeneralBrowserTemplate, SearchableSoupTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def search_novel_in_scraper(self, query: str):
        tags = self.select_search_items(query)
        return list(self.process_search_results(tags))

    def search_novel_in_browser(self, query: str) -> List[SearchResult]:
        tags = self.select_search_items_in_browser(query)
        return list(self.process_search_results(tags))

    @abstractmethod
    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        raise FallbackToBrowser()

    @abstractmethod
    def select_search_items_in_browser(self, query: str) -> Generator[Tag, None, None]:
        """Select novel items found by the query using the browser"""
        raise NotImplementedError()
