import logging
from abc import abstractmethod

from ...core.exeptions import FallbackToBrowser, ScraperErrorGroup
from .general import GeneralBrowserTemplate

logger = logging.getLogger(__name__)


class LoginBrowserTemplate(GeneralBrowserTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def login(self, email: str, password: str) -> None:
        try:
            return self.login_in_scraper(email, password)
        except ScraperErrorGroup:
            return self.login_in_browser(email, password)

    def login_in_scraper(self, email: str, password: str) -> None:
        """Login to the website using the scraper"""
        raise FallbackToBrowser()

    @abstractmethod
    def login_in_browser(self, email: str, password: str) -> None:
        """Login to the website using the browser"""
        raise NotImplementedError()
