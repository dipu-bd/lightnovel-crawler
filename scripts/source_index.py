#!/usr/bin/env python3
"""
Build lightnovel-crawler source index to use for update checking.
"""
import json
from pathlib import Path

WORKDIR = Path(__file__).parent.parent

INDEX_FILE = WORKDIR / 'sources' / 'index.json'
SOURCES_FOLDER = ''
