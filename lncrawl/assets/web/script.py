# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).parent

with open(str(ROOT / 'script.js'), 'r', encoding='utf8') as f:
    script = f.read()
# end with


def get_value():
    return script
# end def
