# -*- coding: utf-8 -*-

import sys
import os
import json
import shutil
import tempfile
import unittest
import logging

from src_v3.app.models import *


class TestModels(unittest.TestCase):
    def tearDown(self):
        logging.shutdown()
        return super().tearDown()

    def test_novel_instance(self):
        url = 'some link'
        novel1 = Novel(url)
        novel2 = Novel(url, name='any name')
        self.assertEqual(novel1, novel2)
        self.assertEqual(novel1.url, url)
        self.assertNotEqual(novel1, Novel('some other link'))

    def test_author_instance(self):
        author1 = Author('John Snow')
        author2 = Author('John Snow')
        self.assertEqual(author1, author2)
        self.assertNotEqual(author1, Author('Jack Snow'))
        self.assertNotEqual(author1, Author(
            'John Snow', author_type=Author.Type.ARTIST))
        self.assertEqual(author1.name, 'John Snow')
        self.assertEqual(author1.type, Author.Type.UNKNOWN)

    def test_novel_properties(self):
        novel = Novel('some url',
                      details='this is detail',
                      name='Novel Name',
                      cover_url='some cover link')
        novel.authors.append(Author('name'))
        self.assertEqual(novel, Novel('some url'))
        self.assertListEqual(novel.authors, [Author('name')])
        self.assertEqual(novel.details, 'this is detail')
        self.assertEqual(novel.name, 'Novel Name')
        self.assertEqual(novel.cover_url, 'some cover link')
        self.assertEqual(novel.language, Language.UNKNOWN)

    def test_language_enum(self):
        self.assertEqual(Language.UNKNOWN.name, 'UNKNOWN')
        self.assertEqual(Language.UNKNOWN.value, '')
        self.assertEqual(Language.ENGLISH.value, 'en')
        self.assertEqual(Language.CHINESE, 'zh')
        self.assertEqual(Language.UNKNOWN, '')
        self.assertEqual(Language.UNKNOWN, Language.UNKNOWN)
        self.assertEqual(str(Language.UNKNOWN), '')
        self.assertEqual(str(Language.CHINESE), 'zh')

    def test_volume_instance(self):
        novel = Novel('any url')
        volume = Volume(novel, serial=2)
        self.assertEqual(volume, volume)
        self.assertEqual(volume, Volume(novel, 2))
        self.assertEqual(volume, Volume(Novel('any url'), 2))
        self.assertNotEqual(volume, Volume(novel, 3))
        self.assertNotEqual(volume, Volume(Novel('other url'), 2))

    def test_volume_properties(self):
        novel = Novel('any url')
        volume = Volume(novel, serial=2,
                        name='vol',
                        details='details')
        self.assertEqual(volume.serial, 2)
        self.assertEqual(volume.novel, novel)
        self.assertEqual(volume.novel, Novel('any url'))
        self.assertEqual(volume.details, 'details')
        self.assertEqual(volume.name, 'vol')

    def test_chapter_instance(self):
        novel = Novel('any url')
        volume = Volume(novel, serial=2)
        chapter = Chapter(volume, serial=205)
        self.assertEqual(chapter, chapter)
        self.assertEqual(chapter, Chapter(volume, 205))
        self.assertNotEqual(chapter, Chapter(volume, 25))
        self.assertNotEqual(chapter, Chapter(Volume(novel, 3), 205))
        self.assertNotEqual(chapter, Chapter(Volume(Novel('an url'), 2), 205))
        self.assertEqual(chapter, Chapter(Volume(Novel('any url'), 2), 205))

    def test_chapter_properties(self):
        novel = Novel('any url')
        volume = Volume(novel, serial=2)
        chapter = Chapter(volume,
                          serial=235,
                          url='url',
                          name='chapter')
        chapter.authors.append(Author('name'))
        chapter.body = '<html>'
        self.assertEqual(volume, chapter.volume)
        self.assertEqual(novel, chapter.novel)
        self.assertEqual(chapter.serial, 235)
        self.assertEqual(chapter.volume.serial, 2)
        self.assertEqual(chapter.novel.url, 'any url')
        self.assertEqual(chapter.name, 'chapter')
        self.assertEqual(chapter.url, 'url')
        self.assertListEqual(chapter.authors, [Author('name')])
        self.assertEqual(chapter.body, '<html>')

    def test_text_direction(self):
        self.assertEqual(TextDirection.LTR.name, 'LTR')
        self.assertEqual(TextDirection.RTL.value, 'rtl')
        self.assertEqual(str(TextDirection.LTR), 'ltr')
        self.assertEqual(TextDirection.RTL, 'rtl')
        self.assertEqual(TextDirection.LTR, TextDirection.LTR)
