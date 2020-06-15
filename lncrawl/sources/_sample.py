# -*- coding: utf-8 -*-

from typing import List

from ..app.models import *
from ..app.scraper.scraper import Scraper


class SampleScraper(Scraper):
    base_urls = ['http://sample.url/']

    def initialize(self) -> None:  # Optional method
        self.log.info('never use print() method')
        pass

    def login(self, email: str, password: str) -> None:  # Optional method
        pass

    def search_novel(self, query: str) -> List[Novel]:  # Optional method
        return []

    def fetch_novel_info(self, url: str) -> Novel:  # Must be implemented
        raise NotImplementedError()

    def fetch_chapter_content(self, chapter: Chapter) -> Chapter:  # Must be implemented
        raise NotImplementedError()
