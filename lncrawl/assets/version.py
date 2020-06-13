# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).parent.parent

with open(str(ROOT / 'VERSION'), 'r') as f:
    version = f.read().strip()
# end with


def get_value():
    return version
# end def
