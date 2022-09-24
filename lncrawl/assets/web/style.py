# -*- coding: utf-8 -*-
import re
from pathlib import Path
from rcssmin import cssmin

ROOT = Path(__file__).parent

with open(str(ROOT / 'style.css'), 'r', encoding='utf8') as f:
    style = f.read()
# end with


def get_value():
    return _minify(style)
# end def


def _minify(css):
    return cssmin(css)
# end def
