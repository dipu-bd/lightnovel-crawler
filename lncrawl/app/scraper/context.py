# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List

from ..binders import OutputFormat
from ..models import *
from .scraper import Scraper
from .sources import get_scraper_by_url


class Context:
    def __init__(self, toc_url: str, text_direction: TextDirection = TextDirection.LTR):
        self.query: str = None
        self.sources_to_query: List[str] = []

        self.toc_url: str = toc_url
        self.text_direction: TextDirection = text_direction
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

    @property
    def scraper(self) -> Scraper:
        if not hasattr(self, '_scraper'):
            self._scraper = get_scraper_by_url(self.toc_url)
        return self._scraper

    def get_chapter_by_url(self, url: str) -> Chapter:
        '''Find the chapter object given url'''
        url = (url or '').strip().strip('/')
        for chapter in self.chapters:
            if chapter.url == url:
                return chapter
        return None
