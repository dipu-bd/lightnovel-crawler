# -*- coding: utf-8 -*-

from .colors import Color
from .version import get_value as get_version
from .default_config import DEFAULT_CONFIG

__all__ = [
    Color,
    get_version,
    DEFAULT_CONFIG,
]
