# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

try:
    from google.protobuf.json_format import MessageToDict
    from google.protobuf.message import Message

    from lncrawl.utils.sonora.client import insecure_web_channel
    from lncrawl.etc import wuxiacom_pb2 as proto
except:
    pass

class WuxiaComCrawler(Crawler):
    base_url = ['https://www.wuxiaworld.com/']

    def initialize(self):
        self.home_url = 'https://www.wuxiaworld.com'
        self.grpc = insecure_web_channel(f"https://api.wuxiaworld.com")
    # end def

    def read_novel_info(self):
        slug = re.findall(r'/novel/([^/]+)', self.novel_url)[0]
        logger.debug('Novel slug: %s', slug)

        client = self.grpc.unary_unary(
            '/wuxiaworld.api.v2.Novels/GetNovel',
            request_serializer=proto.GetNovelRequest.SerializeToString,
            response_deserializer=proto.GetNovelResponse.FromString,
        )
        response = client(proto.GetNovelRequest(slug=slug))
        assert isinstance(response, Message)
        novel = MessageToDict(response)['item']

        self.novel_title = novel['name']
        logger.info('Novel title = %s', self.novel_title)
        
        self.novel_cover = novel['coverUrl']['value']
        logger.info('Novel cover = %s', self.novel_cover)

        self.novel_author = novel['authorName']['value']
        logger.info('Novel author = %s', self.novel_author)

        client = self.grpc.unary_unary(
            '/wuxiaworld.api.v2.Chapters/GetChapterList',
            request_serializer=proto.GetChapterListRequest.SerializeToString,
            response_deserializer=proto.GetChapterListResponse.FromString,
        )
        response = client(proto.GetChapterListRequest(novelId=novel['id']))
        volumes = MessageToDict(response)['items']
        
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
        client = self.grpc.unary_unary(
            '/wuxiaworld.api.v2.Chapters/GetChapter',
            request_serializer=proto.GetChapterRequest.SerializeToString,
            response_deserializer=proto.GetChapterResponse.FromString,
        )
        property = proto.GetChapterByProperty(chapterId=chapter['entityId'])
        response = client(proto.GetChapterRequest(chapterProperty=property))
        chapter = MessageToDict(response)['item']
        
        soup = self.make_soup('<main>' + chapter['content']['value'] + '</main>')
        body = soup.find('main')
        self.clean_contents(body)
        return str(body)
    # end def
# end class
