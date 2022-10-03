from abc import abstractmethod
from typing import Generator, Iterable

from bs4 import BeautifulSoup, Tag

from ...core.crawler import Crawler
from ...models import SearchResult


class SearchableSoupTemplate(Crawler):
    is_template = True

    def search_novel(self, query) -> Iterable[SearchResult]:
        soup = self.get_search_page_soup(query)
        tags = self.select_search_items(soup)
        results = []
        for sr in self.process_search_results(tags):
            if len(results) >= 10:
                break
            if not sr:
                continue
            results.append(sr)
        return results

    def process_search_results(self, tags: Iterable[Tag]) -> Generator[Tag, None, None]:
        """Process novel item tag and generates search results"""
        for tag in tags[:10]:
            if not isinstance(tag, Tag):
                continue
            yield self.parse_search_item(tag)

    @abstractmethod
    def get_search_page_soup(self, query: str) -> BeautifulSoup:
        """Get the search page soup from the query"""
        raise NotImplementedError()

    @abstractmethod
    def select_search_items(self, soup: BeautifulSoup) -> Iterable[Tag]:
        """Select novel items found in search page soup"""
        raise NotImplementedError()

    @abstractmethod
    def parse_search_item(self, tag: Tag) -> SearchResult:
        """Parse a tag and return single search result"""
        raise NotImplementedError()
