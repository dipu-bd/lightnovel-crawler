#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
from urllib.parse import urlparse, quote
from ..utils.crawler import Crawler

logger = logging.getLogger('BABELCHAIN')
search_url = 'https://novel.babelchain.org/api/books?page=0&pageSize=10&fields=id,name,canonicalName,lastChapter&ignoreStatus=false&query=%s'
novel_page_url = 'https://novel.babelchain.org/api/books/%s'
chapter_list_url = 'https://novel.babelchain.org/api/books/%s/chapters?bookId=%s&fields=id,name,canonicalName,hasContent'
chapter_page_url = 'https://novel.babelchain.org/books/%s/chapters/%s'
chapter_json_url = 'https://novel.babelchain.org/api/books/%s/chapters/%s?ignoreTopic=true'


class BabelchainCrawler(Crawler):
    def search_novel(self, query):
        query = query.lower()
        query = '(name:*%s* OR alias:*%s*)' % (query, query)
        url = search_url % quote(query)
        logger.debug('Visiting %s', url)
        data = self.get_json(url)

        results = []
        for item in data['data']:
            if not item['canonicalName']:
                continue
            # end if
            results.append({
                'title': item['name'],
                'url': novel_page_url % item['canonicalName'],
                'info': 'Latest: %s' % item['lastChapter']['name'],
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        # Determine cannonical novel name
        path_fragments = urlparse(self.novel_url).path.split('/')
        if path_fragments[1] == 'books':
            self.novel_hash = path_fragments[2]
        else:
            self.novel_hash = path_fragments[-1]
        # end if
        self.novel_url = novel_page_url % self.novel_hash
        logger.info('Canonical name: %s', self.novel_hash)

        logger.debug('Visiting %s', self.novel_url)
        data = self.get_json(self.novel_url)

        self.novel_id = data['data']['id']
        logger.info('Novel ID: %s', self.novel_id)

        self.novel_title = data['data']['name']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = data['data']['cover']
        logger.info('Novel cover: %s', self.novel_cover)

        list_url = chapter_list_url % (self.novel_id, self.novel_id)
        logger.debug('Visiting %s', list_url)
        data = self.get_json(list_url)

        for item in data['data']:
            # if not item['hasContent']:
            #     logger.debug('No content: %s', item['name'])
            #     continue
            # # end if
            self.chapters.append({
                'id': len(self.chapters) + 1,
                'volume': len(self.chapters)//100 + 1,
                'title': item['name'],
                'url': chapter_page_url % (self.novel_hash, item['canonicalName']),
                'json_url': chapter_json_url % (self.novel_hash, item['canonicalName']),
            })
        # end for

        logger.debug(self.chapters)

        self.volumes = [
            {'id': x + 1}
            for x in range(len(self.chapters) // 100 + 1)
        ]
        logger.debug(self.volumes)

        logger.info('%d volumes and %d chapters found',
                    len(self.volumes), len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting %s', chapter['json_url'])
        data = self.get_json(chapter['json_url'])
        content = data['data']['content']
        content = re.sub(r'<\/?blockquote>', '', content)
        body = [p.strip() for p in content.split('\n\n') if p.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
