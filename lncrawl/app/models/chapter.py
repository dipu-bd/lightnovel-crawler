# -*- coding: utf-8 -*-

from ..utility.url_utils import UrlUtils
from .novel import Novel
from .volume import Volume


class Chapter:
    '''Details of a chapter of a novel'''

    def __init__(self, volume: Volume, serial: int, body_url: str = '') -> None:
        self.volume: Volume = volume
        self.serial: int = serial
        self.name: str = f'Chapter {serial:03}'
        self.body_url: str = body_url
        self.body: str = None

    def __eq__(self, other) -> bool:
        if isinstance(other, Chapter):
            return self.serial == other.serial and self.volume == other.volume
        else:
            return super().__eq__(other)

    def __str__(self) -> str:
        return f"<Chapter volume_name:'{self.volume.name}' serial:{self.serial} name:'{self.name}' url:'{self.body_url}' has_body:{self.has_body}>"

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
        self._name = value.strip() if value else 'N/A'

    @property
    def body_url(self):
        return self._body_url

    @body_url.setter
    def body_url(self, value):
        self._body_url = UrlUtils.join(self.novel.url, value) if value else ''
