# -*- coding: utf-8 -*-

from typing import Any, Dict

from .novel import Novel


class Volume:
    '''Details of a volume (collection of chapters) of a novel'''

    def __init__(self, novel: Novel, serial: int) -> None:
        self.novel = novel
        self.serial: int = int(serial)
        self.name: str = ''
        self.details: str = ''
        self.extra: Dict[Any, Any] = dict()

    def __hash__(self):
        return hash((self.serial, self.novel))

    def __eq__(self, other) -> bool:
        if isinstance(other, Volume):
            return self.serial == other.serial and self.novel == other.novel
        else:
            return super().__eq__(other)

    def __str__(self) -> str:
        return f"<Volume serial:{self.serial} name:'{self.name}' novel:'{self.novel.name}'>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value:
            self._name = value.strip()
        else:
            self._name = "Volume %02d" % self.serial

    def get_extra(self, key: str):
        return self.extra.get(key, '')

    def put_extra(self, key: str, val: Any):
        self.extra[key] = val
