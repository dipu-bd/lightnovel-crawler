# -*- coding: utf-8 -*-

from lncrawl.app.models import Author, Chapter, Language, Novel, TextDirection, Volume, AuthorType


class TestModels:

    def test_novel_instance(self):
        url = 'some link'
        novel1 = Novel(url)
        novel2 = Novel(url, name='any name')
        assert novel1 == novel2
        assert novel1.url == url
        assert novel1 != Novel('some other link')

    def test_author_instance(self):
        author1 = Author('John Snow')
        author2 = Author('John Snow')
        assert author1 == author2
        assert author1 != Author('Jack Snow')
        assert author1 != Author('John Snow', author_type=AuthorType.ARTIST)
        assert author1.name == 'John Snow'
        assert author1.type == AuthorType.UNKNOWN

    def test_novel_properties(self):
        novel = Novel('some url',
                      details='this is detail',
                      name='Novel Name',
                      cover_url='some cover link')
        novel.authors.append(Author('name'))
        assert novel == Novel('some url')
        assert novel.authors == [Author('name')]
        assert novel.details == 'this is detail'
        assert novel.name == 'Novel Name'
        assert novel.cover_url == 'some cover link'
        assert novel.language == Language.UNKNOWN

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
        novel = Novel('any url')
        volume = Volume(novel, serial=2)
        assert volume == volume
        assert volume == Volume(novel, 2)
        assert volume == Volume(Novel('any url'), 2)
        assert volume != Volume(novel, 3)
        assert volume != Volume(Novel('other url'), 2)

    def test_volume_properties(self):
        novel = Novel('any url')
        volume = Volume(novel, serial=2,
                        name='vol',
                        details='details')
        assert volume.serial == 2
        assert volume.novel == novel
        assert volume.novel == Novel('any url')
        assert volume.details == 'details'
        assert volume.name == 'vol'

    def test_chapter_instance(self):
        novel = Novel('any url')
        volume = Volume(novel, serial=2)
        chapter = Chapter(volume, serial=205)
        assert chapter == chapter
        assert chapter == Chapter(volume, 205)
        assert chapter != Chapter(volume, 25)
        assert chapter != Chapter(Volume(novel, 3), 205)
        assert chapter != Chapter(Volume(Novel('an url'), 2), 205)
        assert chapter == Chapter(Volume(Novel('any url'), 2), 205)

    def test_chapter_properties(self):
        novel = Novel('any url')
        volume = Volume(novel, serial=2)
        chapter = Chapter(volume,
                          serial=235,
                          url='url',
                          name='chapter')
        chapter.authors.append(Author('name'))
        chapter.body = '<html>'
        assert volume == chapter.volume
        assert novel == chapter.novel
        assert chapter.serial == 235
        assert chapter.volume.serial == 2
        assert chapter.novel.url == 'any url'
        assert chapter.name == 'chapter'
        assert chapter.url == 'url'
        assert chapter.authors == [Author('name')]
        assert chapter.body == '<html>'

    def test_text_direction(self):
        assert TextDirection.LTR.name == 'LTR'
        assert TextDirection.RTL.value == 'rtl'
        assert str(TextDirection.LTR) == 'ltr'
        assert TextDirection.RTL == 'rtl'
        assert TextDirection.LTR == TextDirection.LTR
