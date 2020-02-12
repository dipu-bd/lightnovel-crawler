# -*- coding: utf-8 -*-
from enum import Enum, auto


class ContentType(Enum):
    SOUP = auto()
    JSON = auto()
    RESPONSE = auto()
    FILE = auto()
