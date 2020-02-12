# -*- coding: utf-8 -*-

from enum import Enum


class StrEnum(str, Enum):
    """Enum where members are also (and must be) strings"""

    def __str__(self):
        return self.value
