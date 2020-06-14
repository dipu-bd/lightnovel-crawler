# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import List
from urllib.parse import urlparse

from ..browser import BrowserResponse, ParallelBrowser
from ..models import Chapter, Novel
from .context import AppContext
from .scrap_step import ScrapStep


class Scraper(ParallelBrowser, metaclass=ABCMeta):
    base_urls: List[str] = []

    def __init__(self, name: str):
        super().__init__(scraper_id=name)

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def login(self, email, password) -> None:
        pass

    @abstractmethod
    def search_novel(self, query) -> List[Novel]:
        pass

    @abstractmethod
    def fetch_novel_info(self) -> Novel:
        pass

    @abstractmethod
    def fetch_chapter_content(self, chapter) -> Chapter:
        pass
