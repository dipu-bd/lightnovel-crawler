# -*- coding: utf-8 -*-

import pytest

from lncrawl.app.models import TextDirection
from lncrawl.app.scraper.context import Context
from lncrawl.app.scraper.scraper import Scraper


class TestScrapers:

    def test_context(self):
        context = Context()
        assert context.novel is None
        assert context.chapters == []
        assert context.volumes == []
        assert context.text_direction == TextDirection.LTR
        assert context != Context()

    def test_scrapper_source_urls(self):
        class Dummy(Scraper):
            def base_urls(self):
                return ['http://some.url']

            def fetch_novel_info(self, url: str) -> Novel:  # Must be implemented
                raise NotImplementedError()

            def fetch_chapter_content(self, chapter: Chapter) -> Chapter:  # Must be implemented
                raise NotImplementedError()

        dummy = Dummy()
        assert dummy.base_urls() == ['http://some.url']
