#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawler WebNovel novels and create epub & mobi files.

[WebNovel](https://www.webnovel.com) is a website of english translated
chinese/korean/japanese light novels. Also known as **Qidian**.
"""
import re
import sys
import json
import requests
from os import path
import concurrent.futures
from .binding import novel_to_kindle
from .helper import get_browser, save_chapter

class WebNovelCrawler:
    '''Crawler for WuxiaWorld'''

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=15)

    def __init__(self, novel_id, start_chapter=None, end_chapter=None):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.novel_id = novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.chapters = []

        self.output_path = path.join('_novel', novel_id)
    # end def


    def start(self):
        '''start crawling'''
        self.get_csrf_token()
        self.get_chapter_list()
        self.get_chapter_bodies()
        novel_to_kindle(self.output_path)
    # end def

    def get_csrf_token(self):
        '''get csrf token'''
        url = 'https://www.webnovel.com/book/' + self.novel_id
        print('Getting CSRF Token from ', url)
        session = requests.Session()
        session.get(url)
        cookies = session.cookies.get_dict()
        self.csrf = cookies['_csrfToken']
        print('CSRF Token =', self.csrf)
    # end def

    def get_chapter_list(self):
        '''get list of chapters'''
        url = 'https://www.webnovel.com/apiajax/chapter/GetChapterList?_csrfToken=' \
              + self.csrf + '&bookId=' + self.novel_id
        print('Getting book name and chapter list...')
        response = requests.get(url)
        response.encoding = 'utf-8'
        data = response.json()
        self.chapters = [x['chapterId'] for x in data['data']['chapterItems']]
        print(len(self.chapters), 'chapters found')
    # end def

    def get_chapter_bodies(self):
        '''get content from all chapters till the end'''
        if not self.start_chapter: return
        start = int(self.start_chapter)
        end = int(self.end_chapter or len(self.chapters))
        start = max(start - 1, 0)
        end = min(end, len(self.chapters))
        if start >= len(self.chapters):
          return print('ERROR: start chapter out of bound.')
        # end if
        future_to_url = {self.executor.submit(self.parse_chapter, index):\
            index for index in range(start, end)}
        # wait till finish
        [x.result() for x in concurrent.futures.as_completed(future_to_url)]
    # end def

    def parse_chapter(self, index):
        chapter_id = self.chapters[index]
        url = 'https://www.webnovel.com/apiajax/chapter/GetContent?_csrfToken=' \
            + self.csrf + '&bookId=' + self.novel_id + '&chapterId=' + chapter_id
        print('Getting chapter...', index + 1, '[' + chapter_id + ']')
        response = requests.get(url)
        response.encoding = 'utf-8'
        data = response.json()
        novel_name = data['data']['bookInfo']['bookName']
        author_name = data['data']['bookInfo']['authorName']
        chapter_title = data['data']['chapterInfo']['chapterName']
        chapter_no = data['data']['chapterInfo']['chapterIndex']
        body = data['data']['chapterInfo']['content']
        body = ''.join(['<p>%s</p>' % x.strip()\
                for x in body.split('\r\n') if len(x.strip())])
        volume_no = ((chapter_no - 1) // 100) + 1
        save_chapter({
            'url': url,
            'novel': novel_name,
            'author': author_name,
            'volume_no': str(volume_no),
            'chapter_no': str(chapter_no),
            'chapter_title': chapter_title,
            'body': '<h1>#%d: %s</h1>%s' % (chapter_no, chapter_title, body)
        }, self.output_path)
        return chapter_id
    # end def
# end class

if __name__ == '__main__':
    WebNovelCrawler(
        novel_id=sys.argv[1],
        start_chapter=sys.argv[2] if len(sys.argv) > 2 else None,
        end_chapter=sys.argv[3] if len(sys.argv) > 3 else None
    ).start()
# end if
