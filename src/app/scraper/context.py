# -*- coding: utf-8 -*-

from enum import Enum
from pathlib import Path
from typing import List

from ..binders import OutputFormat
from ..models import Chapter, Novel, Volume, TextDirection


class AppContext:
    def __init__(self):
        self.query: str = None
        self.sources_to_query: List[str] = []

        self.toc_url: str = None
        self.text_direction: TextDirection = TextDirection.LTR
        self.novel: Novel = None
        self.volumes: List[Volume] = []
        self.chapters: List[Chapter] = []
        self.chapters_to_download: List[int] = []

        self.output_path: Path = None
        self.keep_old_outputs: bool = True
        self.generate_single_book: bool = True
        self.filename_prefix: str = None
        self.filename_suffix: str = None
        self.output_formats: List[OutputFormat] = [OutputFormat.EPUB]
