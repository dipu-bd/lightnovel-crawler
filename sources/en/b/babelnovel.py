# -*- coding: utf-8 -*-
import json
import logging
from concurrent import futures
from urllib.parse import quote, urlparse

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
    base_url = ['https://babelnovel.com/',
                'https://api.babelnovel.com']

    def initialize(self):
        self.home_url = 'https://babelnovel.com/'

    def login(self, email, password):
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

            info = None
            if item['lastChapter']:
                info = 'Latest: %s' % item['lastChapter']['name']

            results.append({
                'title': item['name'],
                'url': novel_page_url % item['canonicalName'],
                'info': info,
            })

        return results

    def read_novel_info(self):
        # Determine cannonical novel name
        path_fragments = urlparse(self.novel_url.rstrip('/')).path.split('/')
        if path_fragments[1] == 'books':
            self.novel_hash = path_fragments[2]
        else:
            self.novel_hash = path_fragments[-1]

        self.novel_url = novel_page_url % self.novel_hash
        logger.info('Canonical name: %s', self.novel_hash)

        logger.debug('Visiting %s', self.novel_url)
        data = self.get_json(self.novel_url)

        self.novel_author = data['data']['author']['enName']
        logger.info('Novel author: %s', self.novel_author)

        self.novel_id = data['data']['id']
        logger.info('Novel ID: %s', self.novel_id)

        self.novel_title = data['data']['name']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = data['data']['cover']
        logger.info('Novel cover: %s', self.novel_cover)

        chapter_count = int(data['data']['releasedChapterCount'])
        self.get_list_of_chapters(chapter_count)

    def get_list_of_chapters(self, chapter_count):
        futures_to_check = dict()
        temp_chapters = dict()
        for page in range(1 + chapter_count // 100):
            list_url = chapter_list_url % (self.novel_id, self.novel_id, page)
            future = self.executor.submit(self.parse_chapter_item, list_url)
            futures_to_check[future] = str(page)

        for future in futures.as_completed(futures_to_check):
            page = int(futures_to_check[future])
            temp_chapters[page] = future.result()

        for page in sorted(temp_chapters.keys()):
            self.volumes.append({'id': page + 1})
            for chap in temp_chapters[page]:
                chap['volume'] = page + 1
                chap['id'] = 1 + len(self.chapters)
                self.chapters.append(chap)

    def parse_chapter_item(self, list_url):
        logger.debug('Visiting %s', list_url)
        data = self.get_json(list_url)
        chapters = list()
        for item in data['data']:
            if not (item['isFree'] or item['isLimitFree'] or item['isBought']):
                continue

            chapters.append({
                'title': item['name'],
                'url': chapter_page_url % (self.novel_hash, item['canonicalName']),
                'json_url': chapter_json_url % (self.novel_hash, item['id']),
            })

        return chapters

    def download_chapter_body(self, chapter):
        data = self.get_json(chapter['json_url'])
        soup = self.make_soup(data['data']['content'].replace('\n', '<br>'))
        body = soup.find('body')
        return self.cleaner.extract_contents(body)
