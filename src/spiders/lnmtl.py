#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for novels from [LNMTL](https://lnmtl.com).
"""
import json
import logging
import re
from concurrent import futures

import js2py
from bs4 import BeautifulSoup

from ..utils.crawler import Crawler

logger = logging.getLogger('LNMTL')

login_url = 'https://lnmtl.com/auth/login'
logout_url = 'https://lnmtl.com/auth/logout'


class LNMTLCrawler(Crawler):
    def login(self, email, password):
        '''login to LNMTL'''
        # Get the login page
        logger.info('Visiting %s', login_url)
        soup = self.get_soup(login_url)
        token = soup.select_one('form input[name="_token"]')['value']
        # Send post request to login
        logger.info('Logging in...')
        response = self.submit_form(
            login_url,
            data=dict(
                _token=token,
                email=email,
                password=password,
            ),
        )
        # Check if logged in successfully
        soup = BeautifulSoup(response.content, 'lxml')
        if soup.select_one('a[href="%s"]' % logout_url):
            print('Logged in')
        else:
            body = soup.select_one('body').text
            logger.debug('-' * 80)
            logger.debug('\n\n'.join([
                x for x in body.split('\n\n')
                if len(x.strip()) > 0
            ]))
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
            self.novel_cover = self.absolute_url(soup.find(
                'img', {'title': self.novel_title})['src'])
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
        matcher_regex = [
            r'^window\.lnmtl = ',
            r'lnmtl\.firstResponse =',
            r'lnmtl\.volumes =',
        ]
        for script in soup.find_all('script'):
            text = script.text.strip()

            mismatch = False
            for match in matcher_regex:
                if not re.search(match, text):
                    mismatch = True
                    break
                # end if
            # end for
            if mismatch:
                continue
            # end if

            try:
                data = js2py.eval_js(
                    '(function() {' + text + 'return window.lnmtl;})()').to_dict()
                logger.debug(data.keys())

                for i, vol in enumerate(data['volumes']):
                    logger.debug(vol)
                    title = vol['title'] if 'title' in vol and vol['title'] else ''
                    title = re.sub(r'[^\u0000-\u00FF]', '', title)
                    title = re.sub(r'\(\)', '', title).strip()
                    self.volumes.append({
                        'id': i + 1,
                        'title': title,
                        'download_id': vol['id'],
                        'volume': int(vol['number']) if 'number' in vol else (i + 1),
                    })
                # end for
            except Exception as err:
                logger.exception('Failed parsing one possible batch')
            # end try
        # end for

        if len(self.volumes) == 0:
            raise Exception('Failed parsing volume list')
        # end if
    # end def

    def download_chapter_list(self):
        self.chapters = []
        page_url = self.absolute_url('/chapter?page=1')
        future_to_url = {
            self.executor.submit(
                self.download_chapter_list_of_volume,
                volume,
                page_url
            ): volume['id']
            for volume in self.volumes
        }
        for future in futures.as_completed(future_to_url):
            futures.wait(future.result())
        # end for
        self.chapters = sorted(self.chapters, key=lambda x: x['id'])
    # end def

    def download_chapter_list_of_volume(self, volume, page_url):
        vol_id = volume['download_id']
        url = '%s&volumeId=%s' % (page_url, vol_id)
        logger.info('Visiting %s', url)
        result = self.get_response(url).json()
        page_url = result['next_page_url']
        for chapter in result['data']:
            self.chapters.append({
                'id': int(chapter['number'] or chapter['position']),
                'url': chapter['site_url'],
                'volume': volume['volume'],
                'title': chapter['title'].strip(),
            })
        # end for
        if result['current_page'] == 1:
            return {
                self.executor.submit(
                    self.download_chapter_list_of_volume,
                    volume,
                    self.absolute_url('/chapter?page=%s' % (page + 1)),
                ): '%s-%s' % (vol_id, page)
                for page in range(1, result['last_page'])
            }
        # end if
        return {}
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
