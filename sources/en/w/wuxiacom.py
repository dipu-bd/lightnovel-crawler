# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

from pyease_grpc import Protobuf, RpcSession


class WuxiaComCrawler(Crawler):
    base_url = ['https://www.wuxiaworld.com/']

    def initialize(self):
        self.home_url = 'https://www.wuxiaworld.com'
        self.grpc = RpcSession(Protobuf.string(WUXIWORLD_PROTO))
    # end def

    def read_novel_info(self):
        slug = re.findall(r'/novel/([^/]+)', self.novel_url)[0]
        logger.debug('Novel slug: %s', slug)

        response = self.grpc.request(
            'https://api.wuxiaworld.com/wuxiaworld.api.v2.Novels/GetNovel',
            {'slug': slug},
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
        )
        response.raise_for_status()
        assert response.single
        chapter = response.single['item']
        
        soup = self.make_soup('<main>' + chapter['content'] + '</main>')
        body = soup.find('main')
        self.clean_contents(body)
        return str(body)
    # end def
# end class


WUXIWORLD_PROTO='''
syntax = "proto3";
package wuxiaworld.api.v2;

import public "google/protobuf/wrappers.proto";

message NovelChapterInfo {
    ChapterItem firstChapter = 1;
    ChapterItem latestChapter = 2;
    google.protobuf.Int32Value chapterCount = 3;
    repeated ChapterGroupItem chapterGroups = 4;
}

message NovelItem {
    int32 id  = 1;
    string name = 2;
    google.protobuf.StringValue coverUrl = 10;
    google.protobuf.StringValue authorName = 13;
    NovelChapterInfo chapterInfo = 23;
}

message ChapterItem {
    int32 entityId = 1;
    string name = 2;
    string slug = 3;
    google.protobuf.StringValue content = 5;
    int32 novelId = 6;
}

message ChapterGroupItem {
    int32 id = 1;
    string title = 2;
    int32 order = 3;
    repeated ChapterItem chapterList = 6;
}


message GetChapterByProperty {
    oneof byProperty {
        int32 chapterId = 1;
        ByNovelAndChapterSlug slugs = 2;
    }

    message ByNovelAndChapterSlug {
        string novelSlug = 1;
        string chapterSlug = 2;
    }
}

message GetNovelRequest {
    oneof selector {
        int32 id = 1;
        string slug = 2;
    }
}

message GetNovelResponse {
    NovelItem item = 1;
}

message GetChapterListRequest {
    int32 novelId = 1;
    FilterChapters filter = 2;

    message FilterChapters {
        google.protobuf.Int32Value chapterGroupId = 1;
        google.protobuf.BoolValue isAdvanceChapter = 2;
    }
}

message GetChapterListResponse {
    repeated ChapterGroupItem items = 1;
}

message GetChapterRequest {
    GetChapterByProperty chapterProperty = 1;
}

message GetChapterResponse {
    ChapterItem item = 1;
}

service Novels {
    rpc GetNovel(GetNovelRequest) returns (GetNovelResponse);
}

service Chapters {
    rpc GetChapterList(GetChapterListRequest) returns (GetChapterListResponse);
    rpc GetChapter(GetChapterRequest) returns (GetChapterResponse);
}
'''
