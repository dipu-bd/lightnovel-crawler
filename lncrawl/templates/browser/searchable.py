from abc import abstractmethod
from typing import Generator, List
from urllib.error import URLError

from bs4 import Tag

from ...models import SearchResult
from ..soup.searchable import SearchableSoupTemplate
from .general import GeneralBrowserTemplate


class SearchableBrowserTemplate(SearchableSoupTemplate, GeneralBrowserTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def search_novel(self, query) -> List[SearchResult]:
        try:
            return super().search_novel()
        except URLError:
            return self.search_novel_in_browser(self.novel_url)

    def search_novel_in_browser(self, query: str) -> List[SearchResult]:
        tags = self.select_search_items(query)
        return list(self.process_search_results(tags))

    @abstractmethod
    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        raise URLError()

    @abstractmethod
    def select_search_items_browser(self, query: str) -> Generator[Tag, None, None]:
        """Select novel items found by the query using the browser"""
        raise NotImplementedError()
