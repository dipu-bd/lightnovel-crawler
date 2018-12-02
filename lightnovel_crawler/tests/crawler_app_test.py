#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler application
"""
import random
import logging
from time import sleep
from lightnovel_crawler.app import start_app
from lightnovel_crawler.utils.crawler import Crawler


class TestCrawler(Crawler):
    @property
    def supports_login(self):
        return True
    # end def

    def login(self, email, password):
        print('Login has been called: email=%s, password=%s' % (email, password))
        sleep(2)
    # end def

    def logout(self):
        print('Logout has been called')
        sleep(1)
    # end def

    def read_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        print('Inside read novel info')
        sleep(1)
        self.novel_title = 'Test Novel'
    # end def

    def download_chapter_list(self):
        '''Download list of chapters and volumes.'''
        print('Download chapter list has been called')
        sleep(1)
        self.volumes = [
            {
                'id': i + 1,
                'title': 'Volume %d' % (i + 1),
            }
            for i in range(5)
        ]
        self.chapters = [
            {
                'id': i + 1,
                'url': str(i + 1),
                'volume': (1 + i // 5),
                'title': 'Chapter %d' % (i + 1),
            }
            for i in range(25)
        ]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        sleep(1)
        return '<p>' + '</p><p>'.join([
            ' '.join([
                ''.join([
                    chr(random.randint(ord('a'), ord('z')))
                    for x in range(random.randint(2, 8))
                ]) for y in range(random.randint(10, 100))
            ]) for z in range(10)
        ]) + '</p>'
    # end def
# end class

def run_tests():
    logging.basicConfig(level=logging.DEBUG)

    print('-' * 80)
    print(' RUNNING TESTS ')
    print('-' * 80)

    start_app({
        'Test App': TestCrawler
    })
# end def


if __name__ == '__main__':
    run_tests()
# end if
