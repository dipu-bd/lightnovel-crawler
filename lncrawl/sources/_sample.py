# -*- coding: utf-8 -*-

import logging
from typing import List

from ..app.models import Chapter, Novel
from ..app.scraper import Scraper

logger = logging.getLogger(__name__)


class SampleScraper(Scraper):
    base_urls = ['http://sample.url/']

    def login(self, email, password) -> None:
        pass

    def search_novel(self, query) -> List[Novel]:
        pass

    def fetch_novel_info(self) -> Novel:
        pass

    def fetch_chapter_content(self, chapter) -> Chapter:
        pass
