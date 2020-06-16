# -*- coding: utf-8 -*-

from typing import List

from .author import Author
from .novel import Novel
from .volume import Volume


class Chapter:
    '''Details of a chapter of a novel'''

    def __init__(self, volume: Volume, serial: int, url: str = '', name: str = None) -> None:
        super().__init__()
        self.volume: Volume = volume
        self.serial: int = serial
        self.url: str = url
        self.name: str = name
        self.body: str = None
        self.authors: List[Author] = []

    def __str__(self) -> str:
        return f"<Chapter serial:{self.serial} volume:{self.volume}>"

    def __eq__(self, other) -> bool:
        if isinstance(other, Chapter):
            return self.serial == other.serial and self.volume == other.volume
        else:
            return super().__eq__(other)

    @property
    def novel(self) -> Novel:
        return self.volume.novel
