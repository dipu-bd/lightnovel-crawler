# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import List

from ..browser import AsyncBrowser
from ..config import CONFIG
from ..models import Chapter
from .context import Context


class Scraper(AsyncBrowser, ABC):
    base_urls: List[str] = []

    def __init__(self, name: str):
        self.name = name
        self.log = logging.getLogger(name)
        super().__init__(CONFIG.scraper(name, 'concurrency/per_scraper/workers'))

    def initialize(self) -> None:
        pass

    def login(self, ctx: Context) -> bool:
        pass

    def search_novels(self, ctx: Context) -> None:
        pass

    @abstractmethod
    def fetch_info(self, ctx: Context) -> None:
        raise NotImplementedError()

    @abstractmethod
    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        raise NotImplementedError()
