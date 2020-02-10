# -*- coding: utf-8 -*-

from .author import Author


class Novel:
    '''Details of a novel'''

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url: str = url
        self.cover_url: str = None
        self.name: str = None
        self.details: str = None
        self.authors: List[Author] = []

    def __str__(self) -> str:
        return f"<Novel url:'{self.url}'>"

    def __eq__(self, other) -> bool:
        if isinstance(other, Novel):
            return self.url == other.url
        else:
            return super().__eq__(other)
