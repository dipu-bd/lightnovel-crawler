# -*- coding: utf-8 -*-

from typing import Any, Dict

from ..utility import UrlUtils
from .novel import Novel
from .volume import Volume


class Chapter:
    '''Details of a chapter of a novel'''

    def __init__(self, volume: Volume, serial: int, body_url: str = '') -> None:
        self.volume: Volume = volume
        self.serial: int = int(serial)
        self.name: str = ''
        self.body_url: str = body_url
        self.body: str = ''
        self.extra: Dict[Any, Any] = dict()

    def __hash__(self):
        return hash((self.serial, self.volume))

    def __eq__(self, other) -> bool:
        if isinstance(other, Chapter):
            return self.serial == other.serial and self.volume == other.volume
        else:
            return super().__eq__(other)

    def __str__(self) -> str:
        return f"<Chapter serial:{self.serial} name:'{self.name}' url:'{self.body_url}' volume:'{self.volume.name}' body_len:{len(self.body)}>"

    @property
    def novel(self) -> Novel:
        return self.volume.novel

    @property
    def has_body(self) -> bool:
        return not self.body

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value:
            self._name = value.strip()
        else:
            self._name = "Chapter %03d" % self.serial

    @property
    def body_url(self):
        return self._body_url

    @body_url.setter
    def body_url(self, value):
        self._body_url = UrlUtils.join(self.novel.url, value) if value else ''

    def get_extra(self, key: str):
        return self.extra[key]

    def put_extra(self, key: str, val: Any):
        self.extra[key] = val
