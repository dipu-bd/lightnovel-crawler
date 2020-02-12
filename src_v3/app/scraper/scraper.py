# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Generator, List, Union

from ..models import *
from .context import AppContext
from .request import Request, RequestType

YieldType = Union[Novel, Volume, Chapter, Author, Language, RequestType]
SendType = Request
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
