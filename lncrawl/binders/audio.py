import logging
import os
from typing import Dict, List

from bs4 import BeautifulSoup

from ..assets.chars import Chars

logger = logging.getLogger(__name__)


def make_mp3s(app, data: Dict[str, List]) -> List[str]:
    mp3_files = []
    
    # TODO: Implement MP3 generation logic
    
    print("Created: %d MP3 files" % len(mp3_files))
    return mp3_files
