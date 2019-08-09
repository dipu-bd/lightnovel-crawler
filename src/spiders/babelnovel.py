# -*- coding: utf-8 -*-
import logging
import re
import json
from urllib.parse import quote, urlparse, unquote

from bs4 import BeautifulSoup
from bs4.element import Tag

from ..utils.crawler import Crawler

logger = logging.getLogger('BABELNOVEL')

search_url = 'https://babelnovel.com/api/books?page=0&pageSize=8&fields=id,name,canonicalName,lastChapter&ignoreStatus=false&query=%s'
novel_page_url = 'https://babelnovel.com/api/books/%s'
chapter_list_url = 'https://babelnovel.com/api/books/%s/chapters?bookId=%s&page=0&pageSize=999999&fields=id,name,canonicalName,hasContent'
chapter_json_url = 'https://babelnovel.com/api/books/%s/chapters/%s?ignoreTopic=true'
chapter_page_url = 'https://babelnovel.com/books/%s/chapters/%s'


class BabelNovelCrawler(Crawler):
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

        self.volumes = [
            {'id': x + 1}
            for x in range(len(self.chapters) // 100 + 1)
        ]

        logger.info('%d volumes and %d chapters found',
                    len(self.volumes), len(self.chapters))
    # end def

    def parse_content_css(self, url):
        soup = self.get_soup(url)
        for script in soup.select('script'):
            text = script.text.strip()
            if not text.startswith('window.__STATE__'):
                continue
            # end if
            content = re.findall('"[^"]+"', text, re.MULTILINE)[0][1:-1]
            data = json.loads(unquote(content))
            cssUrl = self.absolute_url(data['chapterDetailStore']['cssUrl'])
            logger.info('Getting %s', cssUrl)
            css = self.get_response(cssUrl).text
            baddies = css.split('\n')[-1].split('{')[0].strip()
            self.bad_selectors = baddies
            break
        # end for
        logger.info('Bad selectors: %s', self.bad_selectors)
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting %s', chapter['json_url'])
        data = self.get_json(chapter['json_url'])

        soup = BeautifulSoup(data['data']['content'], 'lxml')
        for tag in soup.select(self.bad_selectors):
            tag.extract()
        # end for

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
