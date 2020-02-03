# -*- coding: utf-8 -*-
import json
import logging
import re
from concurrent import futures
from urllib.parse import quote, unquote, urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag

from ..utils.crawler import Crawler

logger = logging.getLogger('BABELNOVEL')

search_url = 'https://babelnovel.com/api/books?page=0&pageSize=8&fields=id,name,canonicalName,lastChapter&ignoreStatus=false&query=%s'
novel_page_url = 'https://babelnovel.com/api/books/%s'
chapter_list_url = 'https://babelnovel.com/api/books/%s/chapters?bookId=%s&page=%d&pageSize=100&fields=id,name,canonicalName,hasContent,isBought,isFree,isLimitFree'
chapter_json_url = 'https://babelnovel.com/api/books/%s/chapters/%s/content'
# https://babelnovel.com/api/books/f337b876-f246-40c9-9bcf-d7f31db00296/chapters/ac1ebce2-e62e-4176-a2e7-6012c606ded4/content
chapter_page_url = 'https://babelnovel.com/books/%s/chapters/%s'


class BabelNovelCrawler(Crawler):
    base_url = 'https://babelnovel.com/'

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
        # to get cookies and session info
        self.parse_content_css(self.home_url)

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

        chapter_count = int(data['data']['chapterCount'])
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
            if not (item['isFree']):  # or item['isLimitFree'] or item['isBought']):
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

    def parse_content_css(self, url):
        try:
            soup = self.get_soup(url)
            content = re.findall('window.__STATE__ = "([^"]+)"', str(soup), re.MULTILINE)
            data = json.loads(unquote(content[0]))
            cssUrl = self.absolute_url(data['chapterDetailStore']['cssUrl'])
            logger.info('Getting %s', cssUrl)
            css = self.get_response(cssUrl).text
            baddies = css.split('\n')[-1].split('{')[0].strip()
            self.bad_selectors = baddies
            logger.info('Bad selectors: %s', self.bad_selectors)
        except:
            self.bad_selectors = []
            logger.exception('Fail to get bad selectors')
        # end for
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting %s', chapter['json_url'])
        data = self.get_json(chapter['json_url'])

        soup = BeautifulSoup(data['data']['content'], 'lxml')
        if self.bad_selectors:
            for tag in soup.select(self.bad_selectors):
                tag.extract()
            # end for
        # end if

        body = soup.find('body')
        self.clean_contents(body)

        for tag in body.contents:
            if not str(tag).strip():
                tag.extract()
            elif isinstance(tag, Tag):
                tag.name = 'p'
            # end if
        # end for

        # body = data['data']['content']
        result = str(body)
        result = re.sub(r'\n\n', '<br><br>', result)
        return result
    # end def
# end class
