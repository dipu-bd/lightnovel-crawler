# -*- coding: utf-8 -*-

import pytest

from src.app.models import TextDirection
from src.app.scraper import (AppContext, ContentType, GeneratorType, Request,
                             RequestType, Scraper)


class TestScrapers:

    def test_request_types(self):
        assert RequestType.CREATE_NOVEL_INSTANCE.name == 'CREATE_NOVEL_INSTANCE'
        assert RequestType.INITIALIZE.value == 1

    def test_content_types(self):
        assert ContentType.SOUP.name == 'SOUP'
        assert ContentType.RESPONSE.value == 3

    def test_context(self):
        context = AppContext()
        assert context.novel is None
        assert context.chapters == []
        assert context.volumes == []
        assert context.text_direction == TextDirection.LTR
        assert context != AppContext()

    def test_request(self):
        request = Request(op=RequestType.INITIALIZE,
                          content={'some': 'body'})
        assert request.op == RequestType.INITIALIZE
        assert request.content_type == ContentType.JSON
        assert request.soup is None
        assert request.json == {'some': 'body'}
        assert request.response is None

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
                some = yield RequestType.INITIALIZE
                assert some == 'body'
                another = yield 42
                assert another == 'last'

        dummy = Dummy()
        gen = dummy.process()
        assert next(gen) == RequestType.INITIALIZE
        assert gen.send('body') == 42
        with pytest.raises(StopIteration):
            gen.send('last')
