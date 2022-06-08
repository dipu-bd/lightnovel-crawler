# -*- coding: utf-8 -*-
import json
import logging
import re

from bs4 import Comment

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

from pyease_grpc import RpcSession


class WuxiaComCrawler(Crawler):
    base_url = ['https://www.wuxiaworld.com/']

    def initialize(self):
        self.home_url = 'https://www.wuxiaworld.com'
        self.grpc = RpcSession.from_descriptor(WUXIWORLD_PROTO)
        self.cleaner.bad_css.clear()
        self.cleaner.bad_tags.add('hr')
        self.bearer_token = None
    # end def

    def login(self, email: str, password: str) -> None:
        self.bearer_token = email + ' ' + password
    # end def

    def read_novel_info(self):
        slug = re.findall(r'/novel/([^/]+)', self.novel_url)[0]
        logger.debug('Novel slug: %s', slug)

        response = self.grpc.request(
            'https://api.wuxiaworld.com/wuxiaworld.api.v2.Novels/GetNovel',
            {'slug': slug},
            headers={ 'authorization': self.bearer_token, }
        )
        response.raise_for_status()
        assert response.single
        novel = response.single['item']

        self.novel_title = novel['name']
        logger.info('Novel title = %s', self.novel_title)
        
        self.novel_cover = novel['coverUrl']
        logger.info('Novel cover = %s', self.novel_cover)

        self.novel_author = novel['authorName']
        logger.info('Novel author = %s', self.novel_author)

        response = self.grpc.request(
            'https://api.wuxiaworld.com/wuxiaworld.api.v2.Chapters/GetChapterList',
            {'novelId': novel['id']},
            headers={ 'authorization': self.bearer_token, }
        )
        response.raise_for_status()
        assert response.single
        volumes = response.single['items']
        
        for group in sorted(volumes, key=lambda x: x.get('order', 0)):
            vol_id = len(self.volumes) + 1
            self.volumes.append({
                'id': vol_id,
                'title': group['title'],
            })
            for chap in group['chapterList']:
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': chap['name'],
                    'entityId': chap['entityId'],
                    'url': 'https://www.wuxiaworld.com/novel/%s/%s' % (slug, chap['slug']),
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        response = self.grpc.request(
            'https://api.wuxiaworld.com/wuxiaworld.api.v2.Chapters/GetChapter',
            {'chapterProperty': {'chapterId': chapter['entityId']}},
            headers={ 'authorization': self.bearer_token, }
        )
        response.raise_for_status()
        assert response.single

        chapter = response.single['item']['content']

        if 'translatorThoughts' in response.single['item']:
            chapter += '<hr/>'
            chapter += "<blockquote><b>Translator's Thoughts</b>"
            chapter += response.single['item']['translatorThoughts']
            chapter += "</blockquote>"

        chapter = re.sub(r'(background-)?color: [^\\";]+', '', chapter)
        return chapter
    # end def
# end class


WUXIWORLD_PROTO=json.loads('''
{"file": [{"name": "google/protobuf/wrappers.proto", "package": "google.protobuf", "messageType": [{"name": "DoubleValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_DOUBLE", "jsonName": "value"}]}, {"name": "FloatValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_FLOAT", "jsonName": "value"}]}, {"name": "Int64Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT64", "jsonName": "value"}]}, {"name": "UInt64Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_UINT64", "jsonName": "value"}]}, {"name": "Int32Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "value"}]}, {"name": "UInt32Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_UINT32", "jsonName": "value"}]}, {"name": "BoolValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "value"}]}, {"name": "StringValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "value"}]}, {"name": "BytesValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BYTES", "jsonName": "value"}]}], "options": {"javaPackage": "com.google.protobuf", "javaOuterClassname": "WrappersProto", "javaMultipleFiles": true, "goPackage": "google.golang.org/protobuf/types/known/wrapperspb", "ccEnableArenas": true, "objcClassPrefix": "GPB", "csharpNamespace": "Google.Protobuf.WellKnownTypes"}, "syntax": "proto3"}, {"name": "wuxia.proto", "package": "wuxiaworld.api.v2", "dependency": ["google/protobuf/wrappers.proto"], "messageType": [{"name": "NovelChapterInfo", "field": [{"name": "firstChapter", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterItem", "jsonName": "firstChapter"}, {"name": "latestChapter", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterItem", "jsonName": "latestChapter"}, {"name": "chapterCount", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Int32Value", "jsonName": "chapterCount"}, {"name": "chapterGroups", "number": 4, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterGroupItem", "jsonName": "chapterGroups"}]}, {"name": "NovelItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "coverUrl", "number": 10, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "coverUrl"}, {"name": "authorName", "number": 13, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "authorName"}, {"name": "chapterInfo", "number": 23, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.NovelChapterInfo", "jsonName": "chapterInfo"}]}, {"name": "ChapterItem", "field": [{"name": "entityId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "entityId"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "slug", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "slug"}, {"name": "content", "number": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "content"}, {"name": "novelId", "number": 6, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "novelId"}, {"name": "translatorThoughts", "number": 19, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "translatorThoughts"}]}, {"name": "ChapterGroupItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "title", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "title"}, {"name": "order", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "order"}, {"name": "chapterList", "number": 6, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterItem", "jsonName": "chapterList"}]}, {"name": "GetChapterByProperty", "field": [{"name": "chapterId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "chapterId"}, {"name": "slugs", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.GetChapterByProperty.ByNovelAndChapterSlug", "oneofIndex": 0, "jsonName": "slugs"}], "nestedType": [{"name": "ByNovelAndChapterSlug", "field": [{"name": "novelSlug", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "novelSlug"}, {"name": "chapterSlug", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "chapterSlug"}]}], "oneofDecl": [{"name": "byProperty"}]}, {"name": "GetNovelRequest", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "id"}, {"name": "slug", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "oneofIndex": 0, "jsonName": "slug"}], "oneofDecl": [{"name": "selector"}]}, {"name": "GetNovelResponse", "field": [{"name": "item", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.NovelItem", "jsonName": "item"}]}, {"name": "GetChapterListRequest", "field": [{"name": "novelId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "novelId"}, {"name": "filter", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.GetChapterListRequest.FilterChapters", "jsonName": "filter"}], "nestedType": [{"name": "FilterChapters", "field": [{"name": "chapterGroupId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Int32Value", "jsonName": "chapterGroupId"}, {"name": "isAdvanceChapter", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isAdvanceChapter"}]}]}, {"name": "GetChapterListResponse", "field": [{"name": "items", "number": 1, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterGroupItem", "jsonName": "items"}]}, {"name": "GetChapterRequest", "field": [{"name": "chapterProperty", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.GetChapterByProperty", "jsonName": "chapterProperty"}]}, {"name": "GetChapterResponse", "field": [{"name": "item", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterItem", "jsonName": "item"}]}, {"name": "UnlockedItem", "field": [{"name": "novelId", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "novelId"}, {"name": "chapterId", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "chapterId"}], "oneofDecl": [{"name": "id"}]}, {"name": "UnlockItemRequest", "field": [{"name": "unlockMethod", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_ENUM", "typeName": ".wuxiaworld.api.v2.UnlockItemMethod", "jsonName": "unlockMethod"}, {"name": "item", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.UnlockedItem", "jsonName": "item"}]}, {"name": "UnlockItemResponse", "field": [{"name": "unlockedItem", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.UnlockedItem", "jsonName": "unlockedItem"}]}], "enumType": [{"name": "UnlockItemMethod", "value": [{"name": "UnlockMethodNone", "number": 0}, {"name": "UnlockMethodKarma", "number": 1}, {"name": "UnlockMethodVip", "number": 2}, {"name": "UnlockMethodSponsor", "number": 3}]}], "service": [{"name": "Novels", "method": [{"name": "GetNovel", "inputType": ".wuxiaworld.api.v2.GetNovelRequest", "outputType": ".wuxiaworld.api.v2.GetNovelResponse"}]}, {"name": "Chapters", "method": [{"name": "GetChapterList", "inputType": ".wuxiaworld.api.v2.GetChapterListRequest", "outputType": ".wuxiaworld.api.v2.GetChapterListResponse"}, {"name": "GetChapter", "inputType": ".wuxiaworld.api.v2.GetChapterRequest", "outputType": ".wuxiaworld.api.v2.GetChapterResponse"}]}, {"name": "Unlocks", "method": [{"name": "UnlockItem", "inputType": ".wuxiaworld.api.v2.UnlockItemRequest", "outputType": ".wuxiaworld.api.v2.UnlockItemResponse"}]}], "publicDependency": [0], "syntax": "proto3"}]}
''')
