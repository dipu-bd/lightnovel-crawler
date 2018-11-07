#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for novels from [LNMTL](https://lnmtl.com).
"""
import re
import logging
import concurrent.futures
from bs4 import BeautifulSoup
from PyInquirer import prompt
from .validators import validateNumber

import sys
import json
import requests
from os import path
from shutil import rmtree
from .helper import save_chapter
from .binding import novel_to_epub, novel_to_mobi

logger = logging.getLogger('LNMTL')

class LNTMLParser:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'lxml')
        self.title = None
    # end def

    def get_title(self):
        try:
            if not self.title:
                SELECTOR = '.novel .media .novel-name'
                self.title = self.soup.select_one(SELECTOR).text.rsplit(' ', 1)[0]
            # end if
        except:
            self.title = 'N/A'
        # end try
        return self.title
    # end def

    def clean_title(self):
        return re.sub(r'[\\/*?:"<>|\']', '', self.get_title()).lower()
    # end def

    def get_cover(self):
        try:
            title = self.get_title()
            return self.soup.find('img', {'title' : title})['src']
        except:
            return ''
        # end try
    # end def

    def get_volumes(self):
        for script in self.soup.find_all('script'):
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
        return self.volumes
    # end def
# end class

class LNTMLCrawler:
    home_url = 'https://lnmtl.com'
    login_url = 'https://lnmtl.com/auth/login'
    logout_url = 'https://lnmtl.com/auth/logout'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    def get_response(self, url):
        return requests.get(
            url,
            headers=self.headers,
            verify=False # whether to verify ssl certs for https
        )
    # end def

    def login(self, email, password):
        '''login to LNMTL'''
        # Get the login page
        logger.debug('Visiting %s', self.login_url)
        response = self.get_response(self.login_url)
        self.headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
        # Send post request to login 
        soup = BeautifulSoup(response.text, 'lxml')
        headers = self.headers.copy()
        headers['content-type'] = 'application/x-www-form-urlencoded'
        body = {
            '_token': soup.select_one('form input[name="_token"]')['value'],
            'email': email,
            'password': password,
        }
        logger.debug('Logging in...')
        response = requests.post(
            self.login_url,
            data=body,
            headers=headers,
            verify=False
        )
        # Update the cookies
        self.headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
        soup = BeautifulSoup(response.text, 'lxml')
        # Check if logged in successfully
        logout = soup.select_one('a[href="%s"]' % self.logout_url)
        if logout is None:
            logger.debug('-' * 80)
            body = soup.select_one('body').text
            logger.debug('\n\n'.join([x for x in body.split('\n\n') if len(x.strip())]))
            logger.debug('-' * 80)
            logger.warning('Failed to login')
        else:
            logger.warning('Logged in')
            self.logged_in = True
        # end if
    # end def

    def logout(self):
        '''logout as a good citizen'''
        logger.debug('Logging out...')
        response = requests.get(self.logout_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        logout = soup.select_one('a[href="%s"]' % self.logout_url)
        if logout is None:
            logger.warning('Logged out.')
        else:
            logger.warning('Failed to logout.')
        # end if
        self.logged_in = False
    # end def

    def read_novel_info(self, url):
        '''get list of chapters'''
        logger.debug('Visiting %s', url)
        parser = LNTMLParser(self.get_response(url).text)
        self.novel_title = parser.get_title()
        self.novel_cover = parser.get_cover()
        self.volumes = parser.get_volumes()
        logger.debug(self.volumes)
        logger.warning('%d volumes found. Loading chapters...', len(self.volumes))
        self.get_chapter_list()
    # end def

    def get_chapter_list(self):
        self.chapters = []
        page_url = '%s/chapter?page=1' % (self.home_url)
        future_to_url = {
            self.executor.submit(
                self.get_chapter_list_by_volume,
                index,
                page_url
            ): index
            for index in range(len(self.volumes))
        }
        for future in concurrent.futures.as_completed(future_to_url):
            concurrent.futures.wait(future.result())
        # end for
        self.chapters = sorted(self.chapters, key=lambda x: int(x['id']))
        logger.debug(self.chapters)
        logger.warning('[%s] %d chapters found', self.novel_title, len(self.chapters))
    # end def

    def get_chapter_list_by_volume(self, vol_index, page_url):
        vol_id = self.volumes[vol_index]['id']
        url = '%s&volumeId=%s' % (page_url, vol_id)
        logger.debug('Visiting %s', url)
        result = self.get_response(url).json()
        page_url = result['next_page_url']
        for chapter in result['data']:
            special = '(Special)' if chapter['is_special'] == '1' else ''
            title = 'Chapter %s %s' % (chapter['number'], special)
            self.chapters.append({
                'id': int(chapter['position']),
                'name': title.strip(),
                'title': chapter['title'],
                'url': chapter['site_url'],
                'volume': self.volumes[vol_index]['title'],
            })
        # end for
        if result['current_page'] == 1:
            return {
                self.executor.submit(
                    self.get_chapter_list_by_volume,
                    vol_index,
                    '%s/chapter?page=%s' % (self.home_url, page + 1)
                ) : '%s-%s' % (vol_id, page)
                for page in range(1, result['last_page'])
            }
        # end if
        return {}
    # end def
# end class

class LNMTLCrawlerApp:
    crawler = LNTMLCrawler()

    def start(self):
        self.login()
        self.novel_info()
        self.chapter_range()
    # end def

    def login(self):
        answer = prompt([
            {
                'type': 'confirm',
                'name': 'login',
                'message': 'Do you want to log in?',
                'default': False
            },
        ])
        if answer['login']:
            answer = prompt([
                {
                    'type': 'input',
                    'name': 'email',
                    'message': 'Email:',
                    'validate': lambda val: 'Email address should be not be empty'
                    if len(val) == 0 else True,
                },
                {
                    'type': 'password',
                    'name': 'password',
                    'message': 'Password:',
                    'validate': lambda val: 'Password should be not be empty'
                    if len(val) == 0 else True,
                },
            ])
            self.crawler.login(answer['email'], answer['password'])
        # end if
    # end def

    def novel_info(self):
        answer = prompt([
            {
                'type': 'input',
                'name': 'novel',
                'message': 'What is the url of novel page?',
                'validate': lambda val: 'Url should be not be empty'
                    if len(val) == 0 else True,
            },
        ])
        self.crawler.read_novel_info(answer['novel'].strip())
    # end def

    def chapter_range(self):
        choices = [
            'Everything!',
            'Last 10 chapters',
            'First 10 chapters',
            'Custom range using URL',
            'Custom range using index',
            'Select specific volumes',
            'Select specific chapters (warning: a large list will be displayed)'
        ]
        answer = prompt([
            {
                'type': 'list',
                'name': 'choice',
                'message': 'Which chapters to download?',
                'choices': choices
            },
        ])
        if choices[0] == answer['choice']:
            pass
        elif choices[1] == answer['choice']:
            self.crawler.chapters = self.crawler.chapters[-10:]
        elif choices[2] == answer['choice']:
            self.crawler.chapters = self.crawler.chapters[:10]
        elif choices[3] == answer['choice']:
           self.chapter_range_urls()
        elif choices[4] == answer['choice']:
            self.chapter_range_numbers()
        elif choices[5] == answer['choice']:
            self.chapter_range_specific_volumes()
        elif choices[6] == answer['choice']:
            self.chapter_range_specific_chapters()
        # end if
        logger.debug('Selected chapters to download')
        logger.debug(self.crawler.chapters)
    # end def

    def chapter_range_urls(self):
        answer = prompt([
            {
                'type': 'input',
                'name': 'start',
                'message': 'Enter start url:',
                'validate': lambda val: 'Url should be not be empty'
                    if len(val) == 0 else True,
            },
            {
                'type': 'input',
                'name': 'stop',
                'message': 'Enter final url:',
                'validate': lambda val: 'Url should be not be empty'
                    if len(val) == 0 else True,
            },
        ])
        start = 0
        stop = len(self.crawler.chapters) - 1
        start_url = answer['start'].strip(' /')
        stop_url = answer['stop'].strip(' /')
        for i, chapter in  enumerate(self.crawler.chapters):
            if chapter['url'] == start_url:
                start = i
            elif chapter['url'] == stop_url:
                stop = i
            # end if
        # end for
        if stop < start:
            start, stop = stop, start
        # end if
        self.crawler.chapters = self.crawler.chapters[start:(stop + 1)]
    # end def

    def chapter_range_numbers(self):
        length = len(self.crawler.chapters)
        answer = prompt([
            {
                'type': 'input',
                'name': 'start',
                'message': 'Enter start index (1 to %d):' % length,
                'validate': lambda val: validateNumber(val, 1, length),
                'filter': lambda val: int(val) - 1,
            },
        ])
        start = answer['start']
        answer = prompt([
            {
                'type': 'input',
                'name': 'stop',
                'message': 'Enter final index (%d to %d):' % (start, length),
                'validate': lambda val: validateNumber(val, start, length),
                'filter': lambda val: int(val) - 1,
            },
        ])
        stop = answer['stop']
        self.crawler.chapters = self.crawler.chapters[start:(stop + 1)]
    # end def

    def chapter_range_specific_volumes(self):
        answer = prompt([
            {
                'type': 'checkbox',
                'name': 'volumes',
                'message': 'Choose volumes to download',
                'choices': [
                    { 'name': vol['title'] }
                    for vol in self.crawler.volumes
                ],
                'validate': lambda ans: 'You must choose at least one volume.' \
                    if len(ans) == 0 else True
            }
        ])
        selected = answer['volumes']
        chapters = [
            chap for chap in self.crawler.chapters
            if selected.count(chap['volume']) > 0
        ]
        self.crawler.start_index = 0
        self.crawler.stop_index = len(chapters)
        self.crawler.chapters = chapters
    # end def

    def chapter_range_specific_chapters(self):
        answer = prompt([
            {
                'type': 'checkbox',
                'name': 'chapters',
                'message': 'Choose chapters to download',
                'choices': [
                    { 'name': '%d - %s' % (chap['id'], chap['title']) }
                    for chap in self.crawler.chapters
                ],
                'validate': lambda ans: 'You must choose at least one chapter.' \
                    if len(ans) == 0 else True
            }
        ])
        selected = [
            int(val.split(' ')[0]) - 1
            for val in answer['chapters']
        ]
        chapters = [
            chap for chap in self.crawler.chapters
            if selected.count(chap['id']) > 0
        ]
        self.crawler.start_index = 0
        self.crawler.stop_index = len(chapters)
        self.crawler.chapters = chapters
    # end def
# end class

"""
class LNMTLCrawler:
    '''Crawler for LNMTL'''

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

    def __init__(self, novel_id, start_chapter=None, end_chapter=None, volume=False, fresh=False):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.chapters = []
        self.novel_id = novel_id
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.output_path = None
        self.pack_by_volume = volume
        self.start_fresh = fresh

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
        if self.start_fresh and path.exists(self.output_path):
            rmtree(self.output_path)
        # end if
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
"""

if __name__ == '__main__':
    LNMTLCrawlerApp().start()
# end if
