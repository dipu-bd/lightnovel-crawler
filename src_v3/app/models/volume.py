# -*- coding: utf-8 -*-

from .novel import Novel


class Volume:
    '''Details of a volume (collection of chapters) of a novel'''

    def __init__(self, novel: Novel, serial: int, name: str = None, details: str = None) -> None:
        super().__init__()
        self.novel: Novel = novel
        self.serial: int = serial
        self.name: str = name
        self.details: str = details

    def __str__(self) -> str:
        return f"<Volume serial:{self.serial} novel:{self.novel}>"

    def __eq__(self, other) -> bool:
        if isinstance(other, Volume):
            return self.serial == other.serial and self.novel == other.novel
        else:
            return super().__eq__(other)
