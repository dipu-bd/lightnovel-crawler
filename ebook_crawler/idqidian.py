#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [Idqidian.us](https://www.idqidian.us/).
"""
import re
import sys
import requests
from os import path
from shutil import rmtree
import concurrent.futures
from bs4 import BeautifulSoup
from .helper import save_chapter
from .binding import novel_to_epub, novel_to_mobi

class IdqidianCrawler:
    '''Crawler for wuxiaworld.co'''

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    def __init__(self, novel_id, start_chapter=None, end_chapter=None, volume=False):
        if novel_id is None:
            raise Exception('Novel ID is required')
        # end if

        self.chapters = []
        self.novel_id = novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.pack_by_volume = volume

        self.home_url = 'https://www.idqidian.us'
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
        url = '%s/orderedra/%s' % (self.home_url, self.novel_id)
        print('Visiting ', url)
        response = requests.get(url, verify=False)
        response.encoding = 'utf-8'
        html_doc = response.text
        print('Getting book name and chapter list... ')
        soup = BeautifulSoup(html_doc, 'lxml')
        # get book name
        try:
            self.novel_name = soup.find_all('span', {"typeof":"v:Breadcrumb"})[-1].text
            #self.novel_cover = self.home_url + soup.find("a", title=re.compile(self.novel_name))['href']
            self.novel_cover = "https://www.idqidian.us/images/noavailable.jpg"
            author = soup.select('p')[3].text
            self.novel_author = author[20:len(author)-22]
        except:
            self.novel_author = 'N/A'
        # end try
        self.output_path = re.sub('[\\\\/*?:"<>|]' or r'[\\/*?:"<>|]', '', self.novel_name or self.novel_id)
        # Get chapter list
        get_ch = lambda x: x.get('href')
        self.chapters = [get_ch(x) for x in soup.find('div', {
            'style': '-moz-border-radius: 5px 5px 5px 5px; border: 1px solid #333; color: black; height: 400px; margin: 5px; overflow: auto; padding: 5px; width: 96%;'}).find_all(
            'a')]
        self.chapters.reverse()
        print(self.chapters[0])
        print(' [%s]' % self.novel_name, len(self.chapters), 'chapters found')
    # end def

    def get_chapter_index(self, chapter):
      if not chapter: return None
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
        #edit if no end url declared then end chapter is lenght of chapter -1 because index started from 0
        self.end_chapter = self.get_chapter_index(self.end_chapter) or (len(self.chapters)-1)
        if self.start_chapter is None: return
        start = self.start_chapter 
        #edit if end url declared then end chapter must be added 1 because when using get chapter index end url has been decreased by 1
        end = min(self.end_chapter, len(self.chapters))+1
        future_to_url = {self.executor.submit(self.parse_chapter, index):\
            index for index in range(start, end)}
        # wait till finish
        [x.result() for x in concurrent.futures.as_completed(future_to_url)]
        print('complete')
    # end def

    def get_volume(self, index):
        url = self.chapters[index]
        chapter_no = index + 1
        volume_no = re.search(r'book-\d+', url)
        if volume_no:
            volume_no = volume_no.group().strip('book-')
        else:
            volume_no = ((chapter_no - 1) // 100) + 1
        # end if
        return volume_no
    # end def

    def parse_chapter(self, index):
        url = self.chapters[index]
        print('Downloading', url)
        response = requests.get(url, verify=False)
        response.encoding = 'utf-8'
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'lxml')
        chapter_no = index + 1
        volume_no = self.get_volume(index)
        chapter_title = soup.select_one('h1').text
        for a in soup.find_all('a'):
            a.decompose()
        body_part = soup.select('p')
        #body_part = ''.join([str(p.extract()) for p in body_part if p.text.strip() and not p.has_attr('style')])
        body_part = ''.join([str(p.extract()) for p in body_part if p.text.strip() and not 'Advertisement' in p.text and not 'JavaScript!' in p.text])
        if body_part =='':
            texts = [str.strip(x) for x in soup.strings if str.strip(x) != '']
            unwanted_text = [str.strip(x.text) for x in soup.find_all()]
            my_texts = set(texts).difference(unwanted_text)
            body_part = ''.join([str(p) for p in my_texts if p.strip() and not 'Advertisement' in p and not 'JavaScript!' in p])
        #end if
        save_chapter({
            'url': url,
            'novel': self.novel_name + ' Bahasa Indonesia',
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
    IdqidianCrawler(
        novel_id=sys.argv[1],
        start_chapter=sys.argv[2] if len(sys.argv) > 2 else None,
        end_chapter=sys.argv[3] if len(sys.argv) > 3 else None,
        volume=sys.argv[4] if len(sys.argv) > 4 else None
    ).start()
# end if
