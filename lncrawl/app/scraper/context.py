# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List

from ..binders import OutputFormat
from ..models import *


class Context:
    def __init__(self, toc_url: str, text_dir: TextDirection = TextDirection.LTR):
        self.query: str = None
        self.search_result: List[Novel] = []

        self.login_id: str = ''
        self.login_password: str = ''
        self.is_logged_in: bool = False

        self.toc_url: str = toc_url
        self.novel = Novel(toc_url)
        self.authors: List[Author] = []
        self.volumes: List[Volume] = []
        self.chapters: List[Chapter] = []
        self.chapters_to_download: List[int] = []
        self.language: Language = Language.UNKNOWN
        self.text_direction: TextDirection = text_dir

        self.output_path: Path = None
        self.keep_old_outputs: bool = True
        self.generate_single_book: bool = True
        self.filename_prefix: str = None
        self.filename_suffix: str = None
        self.output_formats: List[OutputFormat] = [OutputFormat.EPUB]

    @property
    def scraper(self):
        if not hasattr(self, '_scraper'):
            from .sources import get_scraper_by_url
            self._scraper = get_scraper_by_url(self.toc_url)
        return self._scraper

    def get_chapter_by_url(self, url: str) -> Chapter:
        '''Find the chapter object given url'''
        url = (url or '').strip().strip('/')
        for chapter in self.chapters:
            if chapter.url == url:
                return chapter
        return None

    def login(self) -> None:
        if self.is_logged_in:
            return
        self.is_logged_in = self.scraper.login(self)

    def search_novels(self) -> None:
        self.scraper.search_novels(self)

    def fetch_info(self) -> None:
        self.scraper.fetch_info(self)

    def fetch_chapter(self, chapter: Chapter):
        self.scraper.fetch_chapter(self, chapter)
