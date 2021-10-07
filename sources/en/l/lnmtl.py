# -*- coding: utf-8 -*-
import logging
import re
from concurrent import futures

import js2py
from bs4 import BeautifulSoup

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

login_url = 'https://lnmtl.com/auth/login'
logout_url = 'https://lnmtl.com/auth/logout'


class LNMTLCrawler(Crawler):
    machine_translation = True
    base_url = 'https://lnmtl.com/'

    def login(self, email, password):
        '''login to LNMTL'''
        # Get the login page
        logger.info('Visiting %s', login_url)
        soup = self.get_soup(login_url)
        token = soup.select_one('form input[name="_token"]')['value']
        # Send post request to login
        logger.info('Logging in...')
        response = self.submit_form(
            login_url, data=dict(
                _token=token, email=email, password=password,),
        )
        # Check if logged in successfully
        soup = BeautifulSoup(response.content, 'lxml')
        if soup.select_one('a[href="%s"]' % logout_url):
            print('Logged in')
        else:
            body = soup.select_one('body').text
            logger.debug('-' * 80)
            logger.debug(
                '\n\n'.join([x for x in body.split(
                    '\n\n') if len(x.strip()) > 0])
            )
            logger.debug('-' * 80)
            logger.error('Failed to login')
        # end if
    # end def

    def logout(self):
        '''logout as a good citizen'''
        logger.debug('Logging out...')
        soup = self.get_soup(logout_url)
        if soup.select_one('a[href="%s"]' % logout_url):
            logger.error('Failed to logout')
        else:
            print('Logged out')
        # end if
    # end def

    def read_novel_info(self):
        '''get list of chapters'''
        logger.info('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        title = soup.select_one('.novel .media .novel-name').text
        self.novel_title = title.rsplit(' ', 1)[0]
        logger.debug('Novel title = %s', self.novel_title)

        try:
            self.novel_cover = self.absolute_url(
                soup.find('img', {'title': self.novel_title})['src']
            )
        except Exception:
            pass  # novel cover is not so important to raise errors
        # end try
        logger.info('Novel cover = %s', self.novel_cover)

        self.parse_volume_list(soup)
        self.volumes = sorted(self.volumes, key=lambda x: x['id'])

        logger.info('Getting chapters...')
        self.download_chapter_list()
    # end def

    def parse_volume_list(self, soup):
        self.volumes = []
        script = soup.find(name='main').find_next_sibling(name='script').string

        try:
            data = js2py.eval_js(
                '(function() {' + script + 'return window.lnmtl;})()'
            ).to_dict()
            for i, vol in enumerate(data['volumes']):
                title = vol.get('title', '') or ''
                title = re.sub(r'[^\u0000-\u00FF]', '', title)
                title = re.sub(r'\(\)', '', title).strip()
                self.volumes.append(
                    {'id': i + 1, 'title': title, 'download_id': vol['id'], }
                )
            # end for
        except Exception as _:
            logger.exception('Failed parsing one possible batch')
        # end try

        if len(self.volumes) == 0:
            raise Exception('Failed parsing volume list')
        # end if
    # end def

    def download_chapter_list(self):
        futures_to_wait = [
            self.executor.submit(self.download_chapters_per_volume, volume)
            for volume in self.volumes
        ]

        possible_chapters = {}
        for future in futures.as_completed(futures_to_wait):
            vol_id, chapters = future.result()
            possible_chapters[vol_id] = chapters
        # end for

        for volume in self.volumes:
            for chapter in possible_chapters[volume['id']]:
                chap = chapter.copy()
                chap['id'] = len(self.chapters) + 1
                chap['volume'] = volume['id']
                self.chapters.append(chap)
            # end for
        # end for
    # end def

    def download_chapters_per_volume(self, volume, page=1):
        url = self.absolute_url(
            '/chapter?page=%s&volumeId=%s' % (page, volume['download_id'])
        )
        logger.info('Getting json: %s', url)
        result = self.get_json(url)

        chapters = []
        for chapter in result['data']:
            title = chapter.get('title') or ''
            if chapter.get('number'):
                title = '#%s %s' % (chapter.get('number'), title)
            # end if
            chapters.append(
                {'title': title, 'url': chapter['site_url'], }
            )
        # end for

        if page != 1:
            return chapters
        # end if

        for page in range(2, result['last_page'] + 1):
            chapters += self.download_chapters_per_volume(volume, page)
        # end for
        return volume['id'], chapters
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        body = soup.select('.chapter-body .translated')
        body = [self.format_text(x.text) for x in body if x]
        body = '\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])
        return body.strip()
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
