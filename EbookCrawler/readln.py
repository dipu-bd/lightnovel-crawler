#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Crawler for novels from [ReadLightNovel](https://www.readlightnovel.org).
"""
import re
import sys
import requests
from os import path
import concurrent.futures
from bs4 import BeautifulSoup
from .binding import novel_to_kindle
from .helper import get_browser, save_chapter

class ReadLightNovelCrawler:
    '''Crawler for ReadLightNovel'''

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=12)

    def __init__(self, novel_id, start_chapter=None, end_chapter=None):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.chapters = []
        self.novel_id = novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter

        self.home_url = 'https://www.readlightnovel.org'
        self.output_path = path.join('_novel', novel_id)

        requests.urllib3.disable_warnings()
    # end def

    def start(self):
        '''start crawling'''
        self.get_chapter_list()
        # self.get_chapter_bodies()
        novel_to_kindle(self.output_path)
    # end def

    def get_chapter_list(self):
        '''get list of chapters'''
        url = '%s/%s' % (self.home_url, self.novel_id)
        print('Visiting ', url)
        response = requests.get(url, verify=False)
        response.encoding = 'utf-8'
        html_doc = response.text
        print('Getting book name and chapter list... ')
        soup = BeautifulSoup(html_doc, 'lxml')
        # get book name
        self.novel_name = soup.select_one('.block-title h1').text
        # get chapter list
        self.chapters = [x.get('href') for x in soup.select('.chapters .chapter-chs li a')]
        print(' [%s]' % self.novel_name, len(self.chapters), 'chapters found')
    # end def

    def get_chapter_index(self, chapter):
      if not chapter: return None
      if chapter.isdigit():
        if 0 < chapter <= len(self.chapters):
          return chapter - 1
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
        self.end_chapter = self.get_chapter_index(self.end_chapter)
        if not self.start_chapter: return
        start = int(self.start_chapter)
        end = int(self.end_chapter or len(self.chapters))
        end = min(end, len(self.chapters))
        future_to_url = {self.executor.submit(self.parse_chapter, index):\
            index for index in range(start, end)}
        # wait till finish
        [x.result() for x in concurrent.futures.as_completed(future_to_url)]
    # end def

    def parse_chapter(self, index):
        url = self.chapters[index]
        print('Visiting ', url)
        response = requests.get(url, verify=False)
        response.encoding = 'utf-8'
        html_doc = response.text
        print('Getting chapter body... ')
        soup = BeautifulSoup(html_doc, 'lxml')
        chapter_title = soup.select_one('.block-title h1').text
        chapter_no = index + 1
        body_part = self.select('.chapter-content3 p')
        volume_no = ((chapter_no - 1) // 100) + 1
        chapter_title = '#%d: %s' % (chapter_no, chapter_title)
        save_chapter({
            'url': url,
            'novel': novel_name,
            'author': author_name,
            'volume_no': str(volume_no),
            'chapter_no': str(chapter_no),
            'chapter_title': chapter_title,
            'body': '<h1>%s</h1>%s' % (chapter_title, body_part)
        }, self.output_path)
        return chapter_id
    # end def

    def format_text(self, text):
        '''make it a valid html'''
        if ('<p>' in text) and ('</p>' in text):
            text = text.replace(r'[ \n\r]+', '\n')
        else:
            # text = text.replace('<p>', '')
            # text = text.replace('</p>', '\n')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            # text = text.replace('&lt;em&gt;', '<em>')
            # text = text.replace('&lt;/em&gt;', '</em>')
            text = text.replace(r'[ \n\r]+', '\n')
            text = '<p>' + '</p><p>'.join(text.split('\n')) + '</p>'
        # end if
        return text.strip()
    # end def
# end class

if __name__ == '__main__':
    ReadLightNovelCrawler(
        novel_id=sys.argv[1],
        start_chapter=sys.argv[2] if len(sys.argv) > 2 else None,
        end_chapter=sys.argv[3] if len(sys.argv) > 3 else None
    ).start()
# end if
