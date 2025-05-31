import logging
from abc import abstractmethod
from io import BytesIO
from typing import Generator, List, Optional

from PIL import Image

from ...core.browser import Browser, By
from ...core.crawler import Crawler
from ...core.exeptions import FallbackToBrowser, ScraperErrorGroup
from ...models import Chapter
from ...models.search_result import SearchResult

logger = logging.getLogger(__name__)


class BasicBrowserTemplate(Crawler):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""
    can_use_browser = True

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
        self.close_browser()
        super().__del__()

    @property
    def browser(self) -> "Browser":
        """
        A webdriver based browser.
        Requires Google Chrome to be installed.
        """
        self.init_browser()
        return self._browser

    def init_browser(self):
        if not self.can_use_browser:
            raise
        if self.using_browser:
            return
        self._max_workers = self.workers
        self.init_executor(1)
        self._browser = Browser(
            headless=self.headless,
            timeout=self.timeout,
            soup_maker=self,
        )
        self._visit = self._browser.visit
        self._browser.visit = self.visit  # type:ignore

    def visit(self, url: str) -> None:
        self._visit(url)
        self.browser._restore_cookies()
        self.last_soup_url = self.browser.current_url

    def close_browser(self):
        if not self.using_browser:
            return
        self._browser.__del__()
        self.init_executor(self._max_workers)

    def search_novel(self, query: str) -> List[SearchResult]:
        try:
            return list(self.search_novel_in_soup(query))
        except ScraperErrorGroup as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed search novel: %s", e)
            self.init_browser()
            return list(self.search_novel_in_browser(query))
        finally:
            self.close_browser()

    def read_novel_info(self) -> None:
        try:
            self.read_novel_info_in_soup()
        except ScraperErrorGroup as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed in read novel info: %s", e)
            self.init_browser()
            self.volumes.clear()
            self.chapters.clear()
            self.read_novel_info_in_browser()
        finally:
            self.close_browser()

    def download_chapters(
        self,
        chapters: List[Chapter],
        fail_fast=False,
    ) -> Generator[Chapter, None, None]:
        # Try to use scraper first (since it is faster)
        try:
            futures = [
                self.executor.submit(self.download_chapter_body_in_soup, chapter)
                for chapter in chapters
            ]
            generator = self.resolve_as_generator(
                futures,
                desc="Chapters",
                unit="item",
                fail_fast=True,
            )
            for index, result in enumerate(generator):
                try:
                    chapter = chapters[index]
                    chapter.body = result
                    self.extract_chapter_images(chapter)
                    chapter.success = True
                except KeyboardInterrupt:
                    return  # failed
                finally:
                    yield chapter
            return  # successfully downloaded all the chapters
        except ScraperErrorGroup as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed in scraper: %s", e)

        # Download the remaining ones in either scraper or browser if failed
        remaining = filter(lambda x: not x.get("success"), chapters)
        for chapter in self.progress_bar(remaining, desc="Chapters", unit="item"):
            chapter.body = ""
            chapter.images = {}
            try:
                chapter.body = self.download_chapter_body(chapter)
                self.extract_chapter_images(chapter)
                chapter.success = True
            except Exception as e:
                logger.error("Failed to get chapter body: %s", e)
                if isinstance(e, KeyboardInterrupt):
                    break
                if fail_fast:
                    raise e
            finally:
                yield chapter

        self.close_browser()

    def download_chapter_body(self, chapter: Chapter) -> str:
        try:
            return self.download_chapter_body_in_soup(chapter)
        except ScraperErrorGroup as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed to download in soup: %s", e)
            self.init_browser()
            return self.download_chapter_body_in_browser(chapter)

    def download_image(self, url: str, headers={}, **kwargs):
        try:
            return super().download_image(url, headers, **kwargs)
        except ScraperErrorGroup as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed in download image: %s", e)
            self.init_browser()
            self._browser.visit(url)
            self.browser.wait("img", By.TAG_NAME)
            png = self.browser.find("img", By.TAG_NAME).screenshot_as_png
            return Image.open(BytesIO(png))

    def search_novel_in_soup(self, query: str) -> Generator[SearchResult, None, None]:
        """Search for novels with `self.scraper` requests"""
        raise FallbackToBrowser()

    def search_novel_in_browser(
        self, query: str
    ) -> Generator[SearchResult, None, None]:
        """Search for novels with `self.browser`"""
        yield from ()

    def read_novel_info_in_soup(self) -> None:
        """Read novel info with `self.scraper` requests"""
        raise FallbackToBrowser()

    @abstractmethod
    def read_novel_info_in_browser(self) -> None:
        """Read novel info with `self.browser`"""
        raise NotImplementedError()

    def download_chapter_body_in_soup(self, chapter: Chapter) -> str:
        """Download the chapter contents using the `self.scraper` requests"""
        raise FallbackToBrowser()

    @abstractmethod
    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        """Download the chapter contents using the `self.browser`"""
        raise NotImplementedError()
