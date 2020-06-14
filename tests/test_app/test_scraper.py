# -*- coding: utf-8 -*-

import pytest

from lncrawl.app.models import TextDirection
from lncrawl.app.scraper import AppContext, GeneratorType, Scraper, ScrapStep


class TestScrapers:

    def test_context(self):
        context = AppContext()
        assert context.novel is None
        assert context.chapters == []
        assert context.volumes == []
        assert context.text_direction == TextDirection.LTR
        assert context != AppContext()

    def test_scrapper_instance(self):
        class Dummy(Scraper):
            def base_urls(self):
                return super().base_urls(self)

            def process(self):
                return super().process()

        dummy = Dummy()
        assert dummy.context is not None
        assert dummy.context.text_direction == 'ltr'
        with pytest.raises(NotImplementedError):
            dummy.base_urls()
        with pytest.raises(NotImplementedError):
            dummy.process()

    def test_scrapper_source_urls(self):
        class Dummy(Scraper):
            def base_urls(self):
                return ['some url']

            def process(self):
                pass

        dummy = Dummy()
        assert dummy.base_urls() == ['some url']

    def test_scrapper_process_generator(self):
        class Dummy(Scraper):
            def base_urls(self):
                pass

            def process(self) -> GeneratorType:
                some = yield ScrapStep.INITIALIZE
                assert some == 'body'
                another = yield 42
                assert another == 'last'

        dummy = Dummy()
        gen = dummy.process()
        assert next(gen) == ScrapStep.INITIALIZE
        assert gen.send('body') == 42
        with pytest.raises(StopIteration):
            gen.send('last')
