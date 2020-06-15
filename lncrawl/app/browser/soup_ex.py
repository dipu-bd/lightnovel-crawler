# -*- coding: utf-8 -*-

import logging
from typing import Any, List, Mapping

from bs4 import BeautifulSoup, Tag

from ..config import CONFIG

logger = logging.getLogger(__name__)


class ExtendedSoup(BeautifulSoup):

    def get_value(self, node: Tag, attr: str = 'text'):
        if not node:
            return ''
        if hasattr(node, 'has_attr') and node.has_attr(attr):
            return str(node.get(attr) or '')
        if hasattr(node, attr):
            return str(getattr(node, attr) or '')
        return ''

    def select_value(self, selector: str, value_of: str = 'text') -> str:
        node = self.select_one(selector)
        text = self.get_value(node, value_of)
        return text.strip()

    def find_value(self, name=None, attrs={}, recursive=True, text=None, value_of: str = 'text') -> str:
        node = self.find(name, attrs, recursive, text)
        text = self.get_value(node, value_of)
        return text.strip()
