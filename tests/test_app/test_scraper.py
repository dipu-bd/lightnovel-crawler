# -*- coding: utf-8 -*-

import pytest

from lncrawl.app.config import CONFIG
from lncrawl.app.models import *
from lncrawl.app.scraper.context import Context
from lncrawl.app.scraper.scraper import Scraper


class TestScrapers:

    def test_context(self):
        url = 'http://novel.toc.url'
        context = Context(url)
        assert context != Context('http://other.url')
        assert context.novel == Novel(url)
        assert context.chapters == []
        assert context.volumes == []
        assert context.text_direction == TextDirection.LTR

    def test_scraper_config(self):
        assert CONFIG.scraper('any', 'concurrency/max_workers') == 10
        assert CONFIG.scraper('en.lnmtl', 'concurrency/max_workers') == 2

    def test_scrapper_source_urls(self):
        class Dummy(Scraper):
            def base_urls(self):
                return ['http://some.url']

            def fetch_info(self, ctx):
                raise NotImplementedError()

            def fetch_chapter(self, ctx, chapter):
                raise NotImplementedError()

        dummy = Dummy('dummy')
        assert dummy.base_urls() == ['http://some.url']
