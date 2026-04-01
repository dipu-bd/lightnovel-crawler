from .cleaner import TextCleaner
from .crawler import Crawler
from .legacy import LegacyCrawler
from .models import Chapter, CombinedSearchResult, Novel, SearchResult, Volume
from .scraper import Scraper
from .soup import PageSoup
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
