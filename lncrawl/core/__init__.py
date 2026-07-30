"""Crawler core: base classes, templates and shared models.

Submodules are imported lazily via ``__getattr__`` so that ``import
lncrawl.core`` (and every source that imports from it) only pays for what it
actually uses — e.g. a ``LegacyCrawler`` source never loads the templates. The
``TYPE_CHECKING`` block keeps these names statically resolvable for pyright.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scraper import PageSoup, Scraper

    from .cleaner import TextCleaner
    from .crawler import Crawler
    from .legacy import LegacyCrawler
    from .models import Chapter, CombinedSearchResult, Novel, SearchResult, Volume
    from .taskman import TaskManager
    from .template import CrawlerTemplate, SoupTemplate

__all__ = [
    "Crawler",
    "PageSoup",
    "Scraper",
    "TaskManager",
    "TextCleaner",
    "Novel",
    "Volume",
    "Chapter",
    "SearchResult",
    "CombinedSearchResult",
    "CrawlerTemplate",
    "LegacyCrawler",
    "SoupTemplate",
]

# name -> submodule (relative to this package, or "scraper" for the external one)
_LAZY: dict[str, str] = {
    "PageSoup": "scraper",
    "Scraper": "scraper",
    "TextCleaner": ".cleaner",
    "Crawler": ".crawler",
    "LegacyCrawler": ".legacy",
    "Chapter": ".models",
    "CombinedSearchResult": ".models",
    "Novel": ".models",
    "SearchResult": ".models",
    "Volume": ".models",
    "TaskManager": ".taskman",
    "CrawlerTemplate": ".template",
    "SoupTemplate": ".template",
}


def __getattr__(name: str) -> Any:
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    package = None if module == "scraper" else __name__
    return getattr(import_module(module, package), name)
