# -*- coding: utf-8 -*-
import json
import logging
import re
from concurrent import futures
from urllib.parse import quote, urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

babelnovel_api = 'https://api.babelnovel.com'
login_url = babelnovel_api + '/v1/user-account/web-login'
search_url = babelnovel_api + '/v1/books?page=0&pageSize=8&fields=id,name,canonicalName,lastChapter&ignoreStatus=false&query=%s'
novel_page_url = babelnovel_api + '/v1/books/%s'
chapter_list_url = babelnovel_api + '/v1/books/%s/chapters?bookId=%s&page=%d&pageSize=100&fields=id,name,canonicalName,isBought,isFree,isLimitFree'
chapter_json_url = babelnovel_api + '/v1/books/%s/chapters/%s/content'
chapter_page_url = 'https://babelnovel.com/books/%s/chapters/%s'


class BabelNovelCrawler(Crawler):
    base_url = 'https://babelnovel.com/'

    def initialize(self):
        self.set_header('Referer', self.home_url)
        self.set_header('Origin', self.home_url.strip())
        self.set_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36')

    def login(self, email, password):
        '''login to LNMTL'''
        logger.info('Visiting %s', self.home_url)
        data = self.post_json(login_url, data=json.dumps({
            'loginType': 'web',
            'password': password,
            'userName': email,
        }), headers={
            'Content-Type': 'application/json;charset=UTF-8',
        })

        self.token = data['data']['loginResult']['token']
        self.set_header('token', self.token)
        logger.debug('Token = %s', self.token)

        self.user_id = data['data']['loginResult']['user']['id']
        self.set_header('x-user-id', self.user_id)
        logger.info('User ID = %s', self.user_id)
    # end def

    def search_novel(self, query):
        # to get cookies
        self.get_response(self.home_url)

        url = search_url % quote(query.lower())
        logger.debug('Visiting: %s', url)
        data = self.get_json(url)

        results = []
        for item in data['data']:
            if not item['canonicalName']:
                continue
            # end if
            info = None
            if item['lastChapter']:
                info = 'Latest: %s' % item['lastChapter']['name']
            # end if
            results.append({
                'title': item['name'],
                'url': novel_page_url % item['canonicalName'],
                'info': info,
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

        chapter_count = int(data['data']['releasedChapterCount'])
        self.get_list_of_chapters(chapter_count)
    # end def

    def get_list_of_chapters(self, chapter_count):
        futures_to_check = dict()
        temp_chapters = dict()
        for page in range(1 + chapter_count // 100):
            list_url = chapter_list_url % (self.novel_id, self.novel_id, page)
            future = self.executor.submit(self.parse_chapter_item, list_url)
            futures_to_check[future] = str(page)
        # end for
        for future in futures.as_completed(futures_to_check):
            page = int(futures_to_check[future])
            temp_chapters[page] = future.result()
        # end for
        for page in sorted(temp_chapters.keys()):
            self.volumes.append({'id': page + 1})
            for chap in temp_chapters[page]:
                chap['volume'] = page + 1
                chap['id'] = 1 + len(self.chapters)
                self.chapters.append(chap)
            # end for
        # end for
    # end def

    def parse_chapter_item(self, list_url):
        logger.debug('Visiting %s', list_url)
        data = self.get_json(list_url)
        chapters = list()
        for item in data['data']:
            if not (item['isFree'] or item['isLimitFree'] or item['isBought']):
                continue
            # end if
            chapters.append({
                'title': item['name'],
                'url': chapter_page_url % (self.novel_hash, item['canonicalName']),
                'json_url': chapter_json_url % (self.novel_hash, item['id']),
            })
        # end for
        return chapters
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting %s', chapter['json_url'])
        data = self.get_json(chapter['json_url'])

        soup = self.make_soup(data['data']['content'])
        body = soup.find('body')
        self.clean_contents(body)

        for tag in body.contents:
            if not str(tag).strip():
                tag.extract()
            elif isinstance(tag, Tag):
                tag.name = 'p'
            # end if
        # end for

        result = str(body)
        result = re.sub(r'\n\n', '<br><br>', result)
        return result
    # end def
# end class
