# -*- coding: utf-8 -*-

from .novel import Novel


class Volume:
    '''Details of a volume (collection of chapters) of a novel'''

    def __init__(self, novel: Novel, serial: int) -> None:
        self.novel = novel
        self.serial: int = serial
        self.name: str = f'Volume {serial:02}'
        self.details: str = ''

    def __eq__(self, other) -> bool:
        if isinstance(other, Volume):
            return self.serial == other.serial
        else:
            return super().__eq__(other)

    def __str__(self) -> str:
        return f"<Volume novel_name:'{self.novel.name}' serial:{self.serial} name:'{self.name}'>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip() if value else 'N/A'
