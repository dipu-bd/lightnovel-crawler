# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Generator, List, Callable

from ..browser import BrowserResponse
from .context import AppContext
from .scrap_step import ScrapStep

YieldType = ScrapStep
SendType = BrowserResponse
GeneratorType = Generator[YieldType, SendType, None]


class Scraper(metaclass=ABCMeta):
    def __init__(self):
        self.context: AppContext = AppContext()

    @abstractstaticmethod
    def base_urls(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def process(self) -> GeneratorType:
        raise NotImplementedError
