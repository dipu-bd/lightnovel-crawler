# -*- coding: utf-8 -*-

import unittest

from src_v3.app.scraper import *
from src_v3.app.models import TextDirection


class TestScrapers(unittest.TestCase):
    def test_request_types(self):
        self.assertEqual(RequestType.CREATE_NOVEL_INSTANCE.name,
                         'CREATE_NOVEL_INSTANCE')
        self.assertEqual(RequestType.INITIALIZE.value, 1)

    def test_content_types(self):
        self.assertEqual(ContentType.SOUP.name, 'SOUP')
        self.assertEqual(ContentType.RESPONSE.value, 3)

    def test_context(self):
        context = AppContext()
        self.assertIsNone(context.novel)
        self.assertListEqual(context.chapters, [])
        self.assertListEqual(context.volumes, [])
        self.assertEqual(context.text_direction, TextDirection.LTR)
        self.assertNotEqual(context, AppContext())

    def test_request(self):
        request = Request(op=RequestType.INITIALIZE,
                          content={'some': 'body'})
        self.assertEqual(request.op, RequestType.INITIALIZE)
        self.assertEqual(request.content_type, ContentType.JSON)
        self.assertIsNone(request.soup)
        self.assertDictEqual(request.json, {'some': 'body'})
        self.assertIsNone(request.response)

    def test_scrapper_instance(self):
        class Dummy(Scraper):
            def base_urls(self):
                return super().base_urls(self)

            def process(self):
                return super().process()

        dummy = Dummy()
        self.assertIsNotNone(dummy.context)
        self.assertEqual(dummy.context.text_direction, 'ltr')
        with self.assertRaises(NotImplementedError):
            dummy.base_urls()
        with self.assertRaises(NotImplementedError):
            dummy.process()

    def test_scrapper_source_urls(self):
        class Dummy(Scraper):
            def base_urls(self):
                return ['some url']

            def process(self):
                pass

        dummy = Dummy()
        self.assertListEqual(dummy.base_urls(), ['some url'])

    def test_scrapper_process_generator(self):
        tester = self

        class Dummy(Scraper):
            def base_urls(self):
                pass

            def process(self) -> GeneratorType:
                some = yield RequestType.INITIALIZE
                tester.assertEqual(some, 'body')
                another = yield 42
                tester.assertEqual(another, 'last')

        dummy = Dummy()
        gen = dummy.process()
        self.assertEqual(next(gen), RequestType.INITIALIZE)
        self.assertEqual(gen.send('body'), 42)
        with self.assertRaises(StopIteration):
            gen.send('last')
