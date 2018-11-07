#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for novels from [WebNovel](https://www.webnovel.com).
"""
import re
import sys
import json
import requests
from os import path
import concurrent.futures
from .helper import save_chapter
from .binding import novel_to_epub, novel_to_mobi

class WebNovelCrawler:
    '''Crawler for WuxiaWorld'''

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=12)

    book_info_url = 'https://www.webnovel.com/book/%s'
    chapter_list_url = 'https://www.webnovel.com/apiajax/chapter/GetChapterList?_csrfToken=%s&bookId=%s'
    chapter_body_url = 'https://www.webnovel.com/apiajax/chapter/GetContent?_csrfToken=%s&bookId=%s&chapterId=%s'

    def __init__(self, novel_id, start_chapter=None, end_chapter=None, volume=None):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.novel_id = novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.pack_by_volume = volume

        self.chapters = []
        self.volume_no = {}
        self.output_path = None
    # end def


    def start(self):
        '''start crawling'''
        try:
            self.get_csrf_token()
            self.get_chapter_list()
            self.get_chapter_bodies()
        finally:
            self.output_path = self.output_path or self.novel_id
            novel_to_epub(self.output_path, self.pack_by_volume)
            novel_to_mobi(self.output_path)
        # end try
    # end def

    def get_csrf_token(self):
        '''get csrf token'''
        url = self.book_info_url % (self.novel_id)
        print('Getting CSRF Token from ', url)
        session = requests.Session()
        session.get(url)
        cookies = session.cookies.get_dict()
        self.csrf = cookies['_csrfToken']
        print('CSRF Token =', self.csrf)
    # end def

    def get_chapter_list(self):
        '''get list of chapters'''
        url = self.chapter_list_url % (self.csrf, self.novel_id)
        print('Getting book name and chapter list...')
        response = requests.get(url)
        response.encoding = 'utf-8'
        data = response.json()
        if 'chapterItems' in data['data']:
            self.chapters = [x['chapterId'] for x in data['data']['chapterItems']]
        elif 'volumeItems' in data['data']:
            self.chapters = []
            self.volume_no = {}
            for vol in data['data']['volumeItems']:
                for x in vol['chapterItems']:
                    self.chapters.append(x['id'])
                    self.volume_no[str(x['index'])] = vol['index']
                # end for
            # end for
        # end if
        print(len(self.chapters), 'chapters found')
    # end def

    def get_chapter_index(self, chapter):
      if chapter is None: return
      if chapter.isdigit():
        chapter = int(chapter)
        if 1 <= chapter <= len(self.chapters):
          return chapter - 1
        # end if
      # end if
      for i, ch_id in enumerate(self.chapters):
        possible_url_substr = '/book/' + self.novel_id + '/' + ch_id
        if possible_url_substr in chapter:
          return i
        # end if
      # end for
      raise Exception('Invalid chapter url')
    # end def

    def get_chapter_bodies(self):
        '''get content from all chapters till the end'''
        if self.start_chapter is None: return
        start = self.get_chapter_index(self.start_chapter)
        end = self.get_chapter_index(self.end_chapter) or len(self.chapters) - 1
        future_to_url = {self.executor.submit(self.parse_chapter, index):\
            index for index in range(start, end + 1)}
        # Wait till finish
        [x.result() for x in concurrent.futures.as_completed(future_to_url)]
    # end def

    def parse_chapter(self, index):
        chapter_id = self.chapters[index]
        url = self.chapter_body_url % (self.csrf, self.novel_id, chapter_id)
        print('Getting chapter...', index + 1, '[' + chapter_id + ']')
        response = requests.get(url)
        response.encoding = 'utf-8'
        data = response.json()
        novel_name = data['data']['bookInfo']['bookName']
        author_name = 'N/A'
        if 'authorName' in data['data']['bookInfo']:
            author_name = data['data']['bookInfo']['authorName']
        if 'authorItems' in data['data']['bookInfo']:
            author_name = ', '.join([x['name'] for x in data['data']['bookInfo']['authorItems']])
        # end if
        chapter_title = data['data']['chapterInfo']['chapterName']
        chapter_no = data['data']['chapterInfo']['chapterIndex']
        contents = data['data']['chapterInfo']['content']
        body_part = self.format_text(contents)
        chapter_title = '#%d: %s' % (chapter_no, chapter_title)
        volume_no = ((chapter_no - 1) // 100) + 1
        if str(index) in self.volume_no:
            volume_no = self.volume_no[str(index)]
        # end if
        if not self.output_path:
            self.output_path = re.sub('[\\\\/*?:"<>|]' or r'[\\/*?:"<>|]', '', novel_name or self.novel_id)
        # end if
        save_chapter({
            'url': url,
            'novel': novel_name,
            'cover': None,
            'author': author_name,
            'volume_no': str(volume_no),
            'chapter_no': str(chapter_no),
            'chapter_title': chapter_title,
            'body': '<h1>%s</h1>%s' % (chapter_title, body_part)
        }, self.output_path, self.pack_by_volume)
    # end def

    def format_text(self, text):
        '''make it a valid html'''
        text = text.replace(r'[ \n\r]+', '\n')
        if ('<p>' not in text) or ('</p>' not in text):
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            text = [x for x in text.split('\n') if len(x.strip())]
            text = '<p>' + '</p><p>'.join(text) + '</p>'
        # end if
        return text.strip()
    # end def
# end class

if __name__ == '__main__':
    WebNovelCrawler(
        novel_id=sys.argv[1],
        start_chapter=sys.argv[2] if len(sys.argv) > 2 else None,
        end_chapter=sys.argv[3] if len(sys.argv) > 3 else None,
        volume=sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else ''
    ).start()
# end if
