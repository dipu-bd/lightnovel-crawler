# -*- coding: utf-8 -*-

from typing import List

from .novel import Novel
from .chapter import Chapter
from .volume import Volume


class Source:
    '''Details of a source'''

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url: str = base_url
        self.novel: str = Novel()
        self.volumes: List[Volume] = []
        self.chapters: List[Chapter] = []

    def __str__(self) -> str:
        return f"<Novel url:'{self.url}'>"

    def __eq__(self, other) -> bool:
        if isinstance(other, Novel):
            return self.url == other.url
        else:
            return super().__eq__(other)
