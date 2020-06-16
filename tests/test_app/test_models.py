# -*- coding: utf-8 -*-

from lncrawl.app.models import Author, Chapter, Language, Novel, TextDirection, Volume, AuthorType


class TestModels:

    def test_novel_instance(self):
        url = 'some link'
        novel1 = Novel(url)
        novel2 = Novel(url)
        novel2.name = 'any'
        assert novel1 == novel2
        assert novel1.url == url
        assert novel1 != Novel('other link')

    def test_author_instance(self):
        author1 = Author('John Snow')
        author2 = Author('John Snow')
        assert author1 == author2
        assert author1 != Author('Jack Snow')
        assert author1 != Author('John Snow', author_type=AuthorType.ARTIST)
        assert author1.name == 'John Snow'
        assert author1.type == AuthorType.UNKNOWN
        assert isinstance(hash(author1), int)
        assert hash(author1) == hash(author2)

    def test_novel_properties(self):
        novel = Novel('http://any.url/path')
        novel.details = 'this is details'
        novel.name = ' Novel Name '
        novel.cover_url = '/cover/url'
        assert novel == Novel('http://any.url/path/')
        assert novel.details == 'this is details'
        assert novel.name == 'Novel Name'
        assert novel.cover_url == 'http://any.url/cover/url'
        assert isinstance(hash(novel), int)

    def test_language_enum(self):
        assert Language.UNKNOWN.name == 'UNKNOWN'
        assert Language.UNKNOWN.value == ''
        assert Language.ENGLISH.value == 'en'
        assert Language.CHINESE == 'zh'
        assert Language.UNKNOWN == ''
        assert Language.UNKNOWN == Language.UNKNOWN
        assert str(Language.UNKNOWN) == ''
        assert str(Language.CHINESE) == 'zh'

    def test_volume_instance(self):
        novel = Novel('http://any.url/path')
        volume = Volume(novel, serial=2)
        volume2 = Volume(Novel('http://any.url/path'), 2)
        volume3 = Volume(Novel('http://other.url/path'), 2)
        assert volume == volume
        assert volume == Volume(novel, 2)
        assert volume == volume2
        assert volume != Volume(novel, 3)
        assert volume != volume3
        assert isinstance(hash(volume), int)
        assert hash(volume) == hash(volume2)
        assert hash(volume) != hash(volume3)

    def test_volume_properties(self):
        novel = Novel('http://any.url')
        volume = Volume(novel, serial=2)
        assert volume.serial == 2
        assert volume.novel == novel
        assert volume.novel == Novel('http://any.url')
        assert volume.details == ''
        assert volume.name == 'Volume 02'

    def test_chapter_instance(self):
        novel = Novel('http://any.url/path')
        volume = Volume(novel, serial=2)
        chapter = Chapter(volume, serial=205)
        chapter2 = Chapter(volume, 205)
        chapter3 = Chapter(Volume(novel, 3), 205)
        chapter4 = Chapter(Volume(Novel('http://any.url/path'), 2), 205)
        assert chapter == chapter
        assert chapter == chapter2
        assert chapter != Chapter(volume, 25)
        assert chapter != chapter3
        assert chapter != Chapter(Volume(Novel('http://any.url'), 2), 205)
        assert chapter == chapter4
        assert isinstance(hash(chapter), int)
        assert hash(chapter) == hash(chapter2)
        assert hash(chapter) != hash(chapter3)
        assert hash(chapter) == hash(chapter4)

    def test_chapter_properties(self):
        novel = Novel('http://any.url/path')
        volume = Volume(novel, serial=2)
        chapter = Chapter(volume, serial=235, body_url='body/url')
        chapter.body = '<html>'
        assert volume == chapter.volume
        assert novel == chapter.novel
        assert chapter.serial == 235
        assert chapter.volume.serial == 2
        assert chapter.novel.url == 'http://any.url/path'
        assert chapter.name == 'Chapter 235'
        assert chapter.body_url == 'http://any.url/path/body/url'
        assert chapter.body == '<html>'

    def test_text_direction(self):
        assert TextDirection.LTR.name == 'LTR'
        assert TextDirection.RTL.value == 'rtl'
        assert str(TextDirection.LTR) == 'ltr'
        assert TextDirection.RTL == 'rtl'
        assert TextDirection.LTR == TextDirection.LTR
