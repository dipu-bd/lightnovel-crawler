#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for novels from [ReadLightNovel](https://www.readlightnovel.org).
"""
import re
import sys
import requests
from os import path
# from shutil import rmtree
import concurrent.futures
from bs4 import BeautifulSoup
from .helper import save_chapter
from .binding import novel_to_epub, novel_to_mobi

class ReadLightNovelCrawler:
    '''Crawler for ReadLightNovel'''

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    #adding new parameter(volume) to give user option to generate single volume for all chapter or divide volume per 100 chapter
    def __init__(self, novel_id, start_chapter=None, end_chapter=None, volume=False):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.chapters = []
        self.novel_id = novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.pack_by_volume = volume

        self.home_url = 'https://www.readlightnovel.org'
        self.output_path = None

        requests.urllib3.disable_warnings()
    # end def

    def start(self):
        '''start crawling'''
        # if path.exists(self.output_path):
        #     rmtree(self.output_path)
        try:
            self.get_chapter_list()
            self.get_chapter_bodies()
        finally:
            self.output_path = self.output_path or self.novel_id
            novel_to_epub(self.output_path, self.pack_by_volume)
            novel_to_mobi(self.output_path)
        # end try
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
        self.novel_author = 'N/A'
        try:
            self.novel_name = soup.select_one('.block-title h1').text
            self.novel_cover = soup.find('img', {"alt" : self.novel_name})['src']
        except:
            pass
        # end try
        self.output_path = re.sub('[\\\\/*?:"<>|]' or r'[\\/*?:"<>|]', '', self.novel_name or self.novel_id)
        # get chapter list
        self.chapters = [x.get('href') for x in soup.select('.chapters .chapter-chs li a')]
        print(' [%s]' % self.novel_name, len(self.chapters), 'chapters found')
    # end def

    def get_chapter_index(self, chapter):
      if chapter is None: return
      if chapter.isdigit():
        chapter = int(chapter)
        if 1 <= chapter <= len(self.chapters):
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
        self.end_chapter = self.get_chapter_index(self.end_chapter) or len(self.chapters) - 1
        if self.start_chapter is None: return
        start = self.start_chapter
        end = min(self.end_chapter, len(self.chapters)) +1
        future_to_url = {self.executor.submit(self.parse_chapter, index):\
            index for index in range(start, end + 1)}
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
        chapter_title = soup.select_one('.block-title h1').text
        body_part = [str(p.extract()) for p in soup.select('.chapter-content3 p') if len(p.text)]
        chapter_no = index + 1
        volume_no = ((chapter_no - 1) // 100) + 1
        body_part = ''.join(body_part)
        save_chapter({
            'url': url,
            'novel': self.novel_name,
            'cover':self.novel_cover,
            'author': self.novel_author,
            'volume_no': str(volume_no),
            'chapter_no': str(chapter_no),
            'chapter_title': chapter_title,
            'body': '<h1>%s</h1>%s' % (chapter_title, body_part)
        }, self.output_path, self.pack_by_volume)
    # end def
# end class

if __name__ == '__main__':
    ReadLightNovelCrawler(
        novel_id=sys.argv[1],
        start_chapter=sys.argv[2] if len(sys.argv) > 2 else None,
        end_chapter=sys.argv[3] if len(sys.argv) > 3 else None,
        volume=sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else ''
    ).start()
# end if
