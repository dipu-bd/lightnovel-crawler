# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import List
from urllib.parse import urlparse

from ..browser import AsyncBrowser
from ..config import CONFIG
from ..models import Chapter, Novel


class Scraper(AsyncBrowser, metaclass=ABCMeta):
    base_urls: List[str] = []

    def __init__(self, name: str):
        self._config = CONFIG.default('concurrency/per_crawler', name)
        super().__init__(self._config.get('workers', 20))

    @ abstractmethod
    def login(self, email, password) -> None:
        pass

    @ abstractmethod
    def search_novel(self, query) -> List[Novel]:
        pass

    @ abstractmethod
    def fetch_novel_info(self) -> Novel:
        pass

    @ abstractmethod
    def fetch_chapter_content(self, chapter) -> Chapter:
        pass
