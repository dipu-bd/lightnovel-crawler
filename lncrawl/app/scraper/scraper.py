# -*- coding: utf-8 -*-

import logging
from abc import ABCMeta, abstractmethod
from typing import List
from urllib.parse import urlparse

from ..browser import AsyncBrowser
from ..config import CONFIG
from ..models import Chapter, Novel


class Scraper(AsyncBrowser, metaclass=ABCMeta):
    base_urls: List[str] = []

    def __init__(self, name: str):
        self.name = name
        self.log = logging.getLogger(name)
        self._config = CONFIG.default('concurrency/per_crawler', name)
        super().__init__(self._config.get('workers', 20))

    def initialize(self) -> None:
        pass

    def login(self, email: str, password: str) -> None:
        pass

    def search_novel(self, query: str) -> List[Novel]:
        return []

    @abstractmethod
    def fetch_novel_info(self, url: str) -> Novel:
        raise NotImplementedError()

    @ abstractmethod
    def fetch_chapter_content(self, chapter: Chapter) -> Chapter:
        raise NotImplementedError()
