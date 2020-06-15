# -*- coding: utf-8 -*-

from typing import List
from urllib.parse import urljoin

from .author import Author
from .language import Language


class Novel:
    '''Details of a novel'''

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url: str = url
        self.name: str = ''
        self.details: str = ''
        self.cover_url: str = ''
        self.authors: List[Author] = []
        self.language: Language = Language.UNKNOWN

    def __eq__(self, other) -> bool:
        if isinstance(other, Novel):
            return self.url == other.url
        else:
            return super().__eq__(other)

    def __str__(self) -> str:
        attrs = ' '.join([
            f"url='{self.url}'",
            f"name='{self.name}'",
            f"cover_url='{self.cover_url}'",
            f"authors=[{', '.join([str(x) for x in self.authors])}",
        ])
        return f"<Novel {attrs}]'>\n{self.details}"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

    @property
    def cover_url(self):
        return self._cover_url

    @cover_url.setter
    def cover_url(self, value):
        self._cover_url = urljoin(self.url, value)
