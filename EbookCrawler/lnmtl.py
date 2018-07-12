#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for novels from [LNMTL](https://lnmtl.com).
"""
import re
import sys
import json
import requests
from os import path
import concurrent.futures
from bs4 import BeautifulSoup
from .binding import novel_to_kindle
from .helper import get_browser, save_chapter

class LNMTLCrawler:
    '''Crawler for LNMTL'''

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    def __init__(self, novel_id, start_chapter=None, end_chapter=None):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.chapters = []
        self.novel_id = novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.output_path = path.join('_novel', novel_id)

        self.home_url = 'https://lnmtl.com'
        self.login_url = 'https://lnmtl.com/auth/login'
        self.logout_url = 'https://lnmtl.com/auth/logout'
        self.email = 'dipu@algomatrix.co'
        self.password = 'twill1123'

        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        requests.urllib3.disable_warnings()
    # end def

    def start(self):
        '''start crawling'''
        try:
            if self.start_chapter:
                # if not self.login():
                #     print('Failed to login')
                # else:
                #     print('Logged in.')
                # # end if
                self.get_chapter_list()
                # self.get_chapter_bodies()
                # self.logout()
            # end if
        finally:
            if path.exists(self.output_path):
                novel_to_kindle(self.output_path)
            # end if
        # end try
    # end def

    def login(self):
        '''login to LNMTL'''
        print('Visiting', self.login_url)
        response = requests.get(self.login_url, headers=self.headers, verify=False)
        self.headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
        soup = BeautifulSoup(response.text, 'lxml')
        headers = self.headers.copy()
        headers['content-type'] = 'application/x-www-form-urlencoded'
        body = {
            '_token': soup.select_one('form input[name="_token"]')['value'],
            'email': self.email,
            'password': self.password
        }
        print('Attempt login...')
        response = requests.post(self.login_url, data=body, headers=headers, verify=False)
        self.headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
        soup = BeautifulSoup(response.text, 'lxml')
        logout = soup.select_one('a[href="%s"]' % self.logout_url)
        return logout is not None
    # end def

    def logout(self):
        '''logout as a good citizen'''
        print('Attempt logout...')
        response = requests.get(self.logout_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        logout = soup.select_one('a[href="%s"]' % self.logout_url)
        if logout is None:
            print('Logged out.')
        else:
            print('Failed to logout.')
        # end if
    # end def

    def get_chapter_list(self):
        '''get list of chapters'''
        url = '%s/novel/%s' % (self.home_url, self.novel_id)
        print('Visiting', url)
        response = requests.get(url, headers=self.headers, verify=False)
        soup = BeautifulSoup(response.text, 'lxml')
        self.novel_name = soup.select_one('.novel .media .novel-name').text
        for script in soup.find_all('script'):
            text = script.text.strip()
            if not text.startswith('window.lnmtl'):
                continue
            # end if
            i,j = text.find('lnmtl.volumes = '),text.find(';lnmtl.route')
            if i <= 0 and j <= i:
                continue
            # end if
            i += len('lnmtl.volumes =')
            self.volumes = json.loads(text[i:j].strip())
        # end for
        print(len(self.volumes), 'volumes found. Getting chapters...')

        self.chapters = []
        future_to_url = {self.executor.submit(self.get_chapters_by_volume, vol['id']):\
            vol['id'] for vol in self.volumes}
        concurrent.futures.as_completed(future_to_url)
        
        print('> [%s]' % self.novel_name, len(self.chapters), 'chapters found')
    # end def

    def get_chapters_by_volume(self, vol_id):
        page_url = '%s/chapter?page=1' % (self.home_url)
        while page_url:
            url = '%s&volumeId=%s' % (page_url, vol_id)
            print('Visiting', url)
            response = requests.get(url, headers=self.headers, verify=False)
            result = response.json()
            page_url = result['next_page_url']
            for chapter in result['data']:
                self.chapters.append(chapter['site_url'])
            # end for
        # end while
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
        print('Finished crawling.')
    # end def

    def parse_chapter(self, index):
        '''Parse the content of the chapter page'''
        url = browser.url
        # parse contents
        titles = browser.find_by_css('div.dashhead-titles')
        novel = titles.find_by_css('.dashhead-subtitle a')[0]['title']
        volume = titles.find_by_css('.dashhead-subtitle').first.text
        chapter = titles.find_by_css('.dashhead-title').first.text
        translated = browser.find_by_css('.chapter-body .translated')
        # format contents
        volume_no = re.search(r'VOLUME #\d+', volume).group().strip('VOLUME #')
        chapter_no = re.search(r'chapter-\d+$', url).group().strip('chapter-')
        body = [self.format_text(x.text.strip()) for x in translated]
        body = '\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])
        # save data
        save_chapter({
            'url': url,
            'novel': novel.strip(),
            'volume_no': volume_no,
            'chapter_no': chapter_no,
            'chapter_title': chapter,
            'body': '<h1>%s</h1>%s' % (chapter, body)
        }, self.output_path)
    # end def

    def format_text(self, text):
        '''formats the text and remove bad characters'''
        text = text.replace(u'\u00ad', '')
        text = re.sub(r'\u201e[, ]*', '&ldquo;', text)
        text = re.sub(r'\u201d[, ]*', '&rdquo;', text)
        text = re.sub(r'[ ]*,[ ]+', ', ', text)
        return text.strip()
    # end def
# end class


if __name__ == '__main__':
    LNMTLCrawler(
        novel_id=sys.argv[1],
        start_chapter=sys.argv[2] if len(sys.argv) > 2 else '',
        end_chapter=sys.argv[3] if len(sys.argv) > 3 else ''
    ).start()
# end if
