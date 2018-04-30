#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Crawler for [WuxiaWorld](http://www.wuxiaworld.com/).
"""
import re
import sys
import requests
from os import path
import concurrent.futures
from bs4 import BeautifulSoup
from .binding import novel_to_kindle
from .helper import get_browser, save_chapter

class WuxiaCrawler:
    '''Crawler for ReadLightNovel'''

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    def __init__(self, novel_id, start_chapter=None, end_chapter=None):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.chapters = []
        self.novel_id = novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter

        self.home_url = 'https://www.wuxiaworld.com'
        self.output_path = path.join('_novel', novel_id)

        requests.urllib3.disable_warnings()
    # end def

    def start(self):
        '''start crawling'''
        try:
            self.get_chapter_list()
            self.get_chapter_bodies()
        finally:
           novel_to_kindle(self.output_path)
        # end try
    # end def

    def get_chapter_list(self):
        '''get list of chapters'''
        url = '%s/novel/%s' % (self.home_url, self.novel_id)
        print('Visiting ', url)
        response = requests.get(url, verify=False)
        response.encoding = 'utf-8'
        html_doc = response.text
        print('Getting book name and chapter list... ')
        soup = BeautifulSoup(html_doc, 'lxml')
        # get book name
        self.novel_name = soup.select_one('.section-content  h4').text
        # get chapter list
        get_ch = lambda x: self.home_url + x.get('href')
        self.chapters = [get_ch(x) for x in soup.select('ul.list-chapters li.chapter-item a')]
        print(' [%s]' % self.novel_name, len(self.chapters), 'chapters found')
    # end def

    def get_chapter_index(self, chapter):
      if not chapter: return None
      if chapter.isdigit():
        chapter = int(chapter)
        if 1 <= chapter <= len(self.chapters):
          return chapter
        else:
          raise Exception('Invalid chapter number')
        # end if
      # end if
      for i, link in enumerate(self.chapters):
        if chapter == link:
          return i
        # end if
      # end for
      raise Exception('Invalid chapter url')
    # end def

    def get_chapter_bodies(self):
        '''get content from all chapters till the end'''
        self.start_chapter = self.get_chapter_index(self.start_chapter)
        self.end_chapter = self.get_chapter_index(self.end_chapter) or len(self.chapters)
        if self.start_chapter is None: return
        start = self.start_chapter - 1
        end = min(self.end_chapter, len(self.chapters))
        future_to_url = {self.executor.submit(self.parse_chapter, index):\
            index for index in range(start, end)}
        # wait till finish
        [x.result() for x in concurrent.futures.as_completed(future_to_url)]
        print('complete')
    # end def

    def parse_chapter(self, index):
        url = self.chapters[index]
        print('Downloading', url)
        response = requests.get(url, verify=False)
        response.encoding = 'utf-8'
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'lxml')
        chapter_no = index + 1
        volume_no = re.search(r'book-\d+', url)
        if volume_no:
            volume_no = volume_no.group().strip('book-')
        else:
            volume_no = ((chapter_no - 1) // 100) + 1
        # end if
        chapter_title = soup.select_one('.panel-default .caption h4').text
        body_part = soup.select('.panel-default .fr-view p')
        body_part = ''.join([str(p.extract()) for p in body_part if p.text.strip()])
        save_chapter({
            'url': url,
            'novel': self.novel_name,
            'author': 'Unknown',
            'volume_no': str(volume_no),
            'chapter_no': str(chapter_no),
            'chapter_title': chapter_title,
            'body': '<h1>%s</h1>%s' % (chapter_title, body_part)
        }, self.output_path)
    # end def
# end class

if __name__ == '__main__':
    ReadLightNovelCrawler(
        novel_id=sys.argv[1],
        start_chapter=sys.argv[2] if len(sys.argv) > 2 else None,
        end_chapter=sys.argv[3] if len(sys.argv) > 3 else None
    ).start()
# end if
