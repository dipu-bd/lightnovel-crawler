# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Dict, List, Set, Union

from ..binders import OutputFormat
from ..models import *


class Context:
    def __init__(self, toc_url: str, text_dir: TextDirection = TextDirection.LTR):
        self.language: Language = Language.UNKNOWN
        self.text_direction: TextDirection = text_dir

        self.query: str = None
        self.search_result: List[Novel] = []

        self.login_id: str = ''
        self.login_password: str = ''
        self.is_logged_in: bool = False

        self.toc_url: str = toc_url
        self.novel = Novel(toc_url)
        self.authors: Set[Author] = set()
        self.download_queue: Set[Chapter] = set()

        self.volumes: Set[Volume] = set()
        self.chapters: Set[Chapter] = set()

        self.output_path: Path = None
        self.keep_old_path: bool = True
        self.split_book_by_volumes: bool = True
        self.output_formats: Set[OutputFormat] = set([OutputFormat.EPUB])
        self.filename_format: str = '%{title} c%{fchap}-%{lchap}.%{ext}'
        # specs: title, fchap, lchap, fvol, lvol, ext, time, url

    #######################################################
    #                Methods for Scrapping                #
    #######################################################

    @property
    def scraper(self):
        if not hasattr(self, '_scraper'):
            from .sources import get_scraper_by_url
            self._scraper = get_scraper_by_url(self.toc_url)
        return self._scraper

    def call(self, method: str, *args, **kwargs):
        if not hasattr(self.scraper, method):
            raise KeyError(f"{self.scraper.__name__} does not have any method: {method}")
        getattr(self.scraper, method)(*args, **kwargs)

    def login(self) -> None:
        if not self.is_logged_in:
            self.is_logged_in = self.scraper.login(self)

    def search_novels(self) -> None:
        self.scraper.search_novels(self)

    def fetch_info(self) -> None:
        self.scraper.fetch_info(self)

    def fetch_chapter(self, chapter: Chapter):
        self.scraper.fetch_chapter(self, chapter)

    #######################################################
    #             Methods to manage volume list           #
    #######################################################

    @property
    def max_volume_serial(self) -> int:
        return max(self.volumes, key=lambda x: x.serial)

    @property
    def min_volume_serial(self) -> int:
        return min(self.volumes, key=lambda x: x.serial)

    def get_volume(self, serial: int) -> Union[Volume, None]:
        probe = Volume(self.novel, serial)
        temp = self.volumes.intersection(set([probe]))
        return temp.pop() if len(temp) == 1 else None

    def add_volume(self, serial: int = None) -> Volume:
        if serial is None:
            serial = self.max_volume_serial + 1
        vol = self.get_volume(serial)
        if vol is None:
            vol = Volume(self.novel, serial)
            self.volumes.add(vol)
        return vol

    #######################################################
    #            Methods to manage chapter list           #
    #######################################################
    @property
    def max_chapter_serial(self) -> int:
        return max(self.chapters, key=lambda x: x.serial)

    @property
    def min_chapter_serial(self) -> int:
        return min(self.chapters, key=lambda x: x.serial)

    def get_chapter(self, serial: int, volume: Volume = None) -> Union[Chapter, None]:
        if volume is not None:
            probe = Chapter(self.volume, serial)
            temp = self.chapters.intersection(set([probe]))
            return temp.pop() if len(temp) == 1 else None
        for chapter in self.chapters:
            if chapter.serial == serial:
                return chapter
        return None

    def add_chapter(self, serial: int = None, volume: Volume = None) -> Volume:
        if serial is None:
            serial = self.max_chapter_serial + 1
        chapter = self.get_chapter(serial, volume)
        if chapter is None:
            if volume is None:
                volume = self.add_volume((serial - 1) / 100)
            chapter = Chapter(volume, serial)
            self.chapters.add(chapter)
        return chapter

    def get_chapter_by_url(self, url: str) -> Union[Chapter, None]:
        '''Find the chapter object given url'''
        url = (url or '').strip().strip('/')
        for chapter in self.chapters:
            if chapter.body_url == url:
                return chapter
        return None
