# -*- coding: utf-8 -*-

from .section import __Section__
from ..arguments import get_args


class _Arguments(__Section__):
    def __init__(self):
        super().__init__(None, '')
        self.__data__ = get_args().__dict__

    @property
    def config(self):
        return self.__data__.get('config')
