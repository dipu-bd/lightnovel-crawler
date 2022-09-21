# -*- coding: utf-8 -*-
import re
from pathlib import Path
from css_html_js_minify import css_minify

ROOT = Path(__file__).parent

with open(str(ROOT / 'style.css'), 'r', encoding='utf8') as f:
    style = f.read()
# end with


def get_value():
    t = css_minify(style)
    return css_minify(style)
# end def
