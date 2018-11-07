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
# from shutil import rmtree
import concurrent.futures
from bs4 import BeautifulSoup
from .helper import save_chapter
from .binding import novel_to_epub, novel_to_mobi

class LNMTLCrawler:
    '''Crawler for LNMTL'''

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

    def __init__(self, novel_id, start_chapter=None, end_chapter=None, volume=False):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.chapters = []
        self.novel_id = novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.output_path = None
        self.pack_by_volume = volume

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
        # if path.exists(self.output_path):
        #     rmtree(self.output_path)
        try:
            if self.start_chapter:
                if not self.login():
                    print('Failed to login')
                else:
                    print('Logged in.')
                # end if
                self.get_chapter_list()
                self.get_chapter_bodies()
                self.logout()
            # end if
        finally:
            self.output_path = self.output_path or self.novel_id
            novel_to_epub(self.output_path, self.pack_by_volume)
            novel_to_mobi(self.output_path)
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
        if logout is None:
            print('-' * 80)
            body = soup.select_one('body').text
            print('\n\n'.join([x for x in body.split('\n\n') if len(x.strip())]))
            print('-' * 80)
            return False
        # end if
        return True
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
        self.novel_author = 'N/A'
        try:
            self.novel_name = soup.select_one('.novel .media .novel-name').text
            self.novel_name = self.novel_name.rsplit(' ', 1)[0]
            self.novel_cover = soup.find('img', {"title" : self.novel_name})['src']
        except:
            self.novel_cover = None
        # end try
        self.output_path = re.sub('[\\\\/*?:"<>|]' or r'[\\/*?:"<>|]', '', self.novel_name or self.novel_id)
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
        future_to_url = {}
        page_url = '%s/chapter?page=1' % (self.home_url)
        for vol in self.volumes:
            task = self.executor.submit(self.get_chapters_by_volume, vol['id'], page_url)
            future_to_url[task] = vol['id']
        # end for
        for future in concurrent.futures.as_completed(future_to_url):
            concurrent.futures.wait(future.result())
        # end for

        self.chapters = sorted(self.chapters, key=lambda x: int(x['position']))
        print('> [%s]' % self.novel_name, len(self.chapters), 'chapters found')
    # end def

    def get_chapters_by_volume(self, vol_id, page_url):
        url = '%s&volumeId=%s' % (page_url, vol_id)
        print('Visiting', url)
        response = requests.get(url, headers=self.headers, verify=False)
        result = response.json()
        page_url = result['next_page_url']
        for chapter in result['data']:
            self.chapters.append(chapter)
        # end for
        future_to_url = {}
        if result['current_page'] == 1:
            for page in range(1, result['last_page']):
                page_url = '%s/chapter?page=%s' % (self.home_url, page + 1)
                task = self.executor.submit(self.get_chapters_by_volume, vol_id, page_url)
                future_to_url[task] = '%s-%s' % (vol_id, page)
            # end for
        # end if
        return future_to_url
    # end def

    def get_chapter_index(self, chapter):
      if chapter is None: return
      for i, chap in enumerate(self.chapters):
        if chap['site_url'] == chapter or chap['number'] == chapter:
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
        start = self.start_chapter - 1
        end = min(self.end_chapter + 1, len(self.chapters))
        future_to_url = {self.executor.submit(self.parse_chapter, index):\
            index for index in range(start, end)}
        # wait till finish
        [x.result() for x in concurrent.futures.as_completed(future_to_url)]
        print('Finished crawling.')
    # end def

    def get_volume(self, vol_id, chapter_no):
        for index, vol in enumerate(self.volumes):
            if vol['id'] == vol_id:
                return vol['name'] if 'name' in vol else str(index + 1)
            # end if
        # end for
        return str(int(chapter_no) // 100)
    # end def

    def parse_chapter(self, index):
        '''Parse the content of the chapter page'''
        url = self.chapters[index]['site_url']
        print('Crawling', url)
        response = requests.get(url, headers=self.headers, verify=False)
        soup = BeautifulSoup(response.text, 'lxml')
        logout = soup.select_one('a[href="%s"]' % self.logout_url)
        if logout is None:
            print('WARNING: not logged in')
        # end if
        volume_no = self.chapters[index]['volume_id']
        chapter_no = self.chapters[index]['position']

        chapter_title = self.chapters[index]['title']
        chapter_title = '#%s %s' % (chapter_no, chapter_title)
        body = soup.select('.chapter-body .translated')
        body = [self.format_text(x.text) for x in body if x]
        body = '\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])
        # save data
        save_chapter({
            'url': url,
            'novel': self.novel_name,
            'cover':self.novel_cover,
            'author': self.novel_author,
            'volume_no': str(volume_no),
            'chapter_no': chapter_no,
            'chapter_title': chapter_title,
            'body': '<h1>%s</h1>%s' % (chapter_title, body)
        }, self.output_path, self.pack_by_volume)
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
        end_chapter=sys.argv[3] if len(sys.argv) > 3 else '',
        volume=sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else ''
    ).start()
# end if
