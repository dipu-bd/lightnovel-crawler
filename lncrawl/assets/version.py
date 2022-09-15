# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).parent.parent

with open(str(ROOT / 'VERSION'), 'r', encoding='utf8') as f:
    version = f.read().strip()


def get_value():
    return version



def get_version():
    return version

