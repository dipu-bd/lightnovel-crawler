import logging
from abc import abstractmethod
from typing import Generator, List, Optional

from cloudscraper.exceptions import CloudflareException

from ...core.browser import Browser
from ...core.crawler import Crawler
from ...core.exeptions import ScraperNotSupported
from ...models import Chapter
from ...models.search_result import SearchResult

logger = logging.getLogger(__name__)


class BasicBrowserTemplate(Crawler):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def __init__(
        self,
        headless: bool = False,
        timeout: Optional[int] = 120,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
    ) -> None:
        self.timeout = timeout
        self.headless = headless
        super().__init__(
            workers=workers,
            parser=parser,
        )

    @property
    def using_browser(self) -> bool:
        return hasattr(self, "_browser") and self._browser.active

    def __del__(self) -> None:
        super().__del__()
        if self.using_browser:
            self._browser.__del__()
            delattr(self, "_browser")

    @property
    def browser(self) -> "Browser":
        """
        A webdriver based browser.
        Requires Google Chrome to be installed.
        """
        self.init_browser()
        return self._browser

    def init_browser(self):
        if self.using_browser:
            return
        self.init_executor(1)
        self._browser = Browser(
            headless=self.headless,
            cookie_store=self.scraper.cookies,
            timeout=self.timeout,
            soup_maker=self,
        )

    def search_novel(self, query: str) -> List[SearchResult]:
        try:
            if self.using_browser:
                raise ScraperNotSupported()
            return list(self.search_novel_in_scraper(query))
        except CloudflareException:
            return list(self.search_novel_in_browser(query))

    def search_novel_in_scraper(
        self, query: str
    ) -> Generator[SearchResult, None, None]:
        """Search for novels with `self.scraper` requests"""
        raise ScraperNotSupported()

    def search_novel_in_browser(
        self, query: str
    ) -> Generator[SearchResult, None, None]:
        """Search for novels with `self.browser`"""
        return []

    def read_novel_info(self) -> None:
        try:
            if self.using_browser:
                raise ScraperNotSupported()
            return self.read_novel_info_in_scraper()
        except CloudflareException:
            return self.read_novel_info_in_browser()

    def read_novel_info_in_scraper(self) -> None:
        """Read novel info with `self.scraper` requests"""
        raise ScraperNotSupported()

    @abstractmethod
    def read_novel_info_in_browser(self) -> None:
        """Read novel info with `self.browser`"""
        raise NotImplementedError()

    def download_chapter_body(self, chapter: Chapter) -> str:
        try:
            if self.using_browser:
                raise ScraperNotSupported()
            return self.download_chapter_body_in_scraper()
        except CloudflareException:
            return self.download_chapter_body_in_browser()

    def download_chapter_body_in_scraper(self, chapter: Chapter) -> str:
        """Download the chapter contents using the `self.scraper` requests"""
        raise ScraperNotSupported()

    @abstractmethod
    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        """Download the chapter contents using the `self.browser`"""
        raise NotImplementedError()
