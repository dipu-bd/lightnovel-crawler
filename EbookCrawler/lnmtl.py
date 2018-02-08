#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawler LNMTL novels and create epub files

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.
"""
import re
import sys
from os import path
from .binding import novel_to_kindle
from .helper import get_browser, save_chapter


class LNMTLCrawler:
    '''Crawler for LNMTL'''

    def __init__(self, novel_id, start_url=None, end_url=None):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.novel_id = novel_id
        self.author_name = 'Sudipto Chandra'

        self.home_url = 'https://lnmtl.com'
        self.login_url = 'https://lnmtl.com/auth/login'
        self.logout_url = 'https://lnmtl.com/auth/logout'
        self.email = 'dipu@algomatrix.co'
        self.password = 'twill1123'

        self.start_url = self.get_url_from_chapter(start_url)
        self.end_url = self.get_url_from_chapter(end_url)

        self.output_path = path.join('_novel', novel_id)
    # end def

    def get_url_from_chapter(self, chapter):
        '''get url from chapter number'''
        if not chapter:
            return None
        # end if
        if chapter.isdigit():
            return '%s/chapter/%s-chapter-%s' % (self.home_url, self.novel_id, chapter)
        else:
            return chapter.strip('/')
    # end def

    def start(self):
        '''start crawling'''
        browser = get_browser()
        try:
            if self.start_url:
                if not self.login(browser):
                    raise Exception('Failed to login')
                # end if
                self.crawl_chapters(browser)
                self.logout(browser)
            # end if
        finally:
            browser.quit()
        # end try
        novel_to_kindle(self.output_path)
    # end def

    def login(self, browser):
        '''login to LNMTL'''
        print('Attempting login:', self.login_url)
        browser.visit(self.login_url)
        browser.find_by_css('form input#email').fill(self.email)
        browser.find_by_css('form input#password').fill(self.password)
        browser.find_by_css('form button[type="submit"]').click()
        return browser.url.strip('/') == self.home_url
    # end def

    def logout(self, browser):
        '''logout as a good citizen'''
        print('Attempting logout:', self.logout_url)
        browser.visit(self.logout_url)
        return browser.url.strip('/') == self.home_url
    # end def

    def crawl_chapters(self, browser):
        '''Crawl all chapters till the end'''
        url = self.start_url
        while url:
            print('Visiting:', url)
            browser.visit(url)
            self.parse_chapter(browser)
            if url == self.end_url:
                break
            # end if
            try:
                url = browser.find_by_css('nav .pager .next a').first['href']
            except:
                url = None
            # end try
        # end while
    # end def

    def parse_chapter(self, browser):
        '''Parse the content of the chapter page'''
        url = browser.url
        # parse contents
        titles = browser.find_by_css('div.dashhead-titles')
        novel = titles.find_by_css('.dashhead-subtitle a')[0]['title']
        volume = titles.find_by_css('.dashhead-subtitle').first.text
        chapter = titles.find_by_css('.dashhead-title').first.text
        translated = browser.find_by_css('.chapter-body .translated')
        # format contents
        chapter = self.format_text(chapter)
        volume_no = re.search(r'\d+$', volume).group()
        chapter_no = re.search(r'\d+$', url).group()
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
        start_url=sys.argv[2] if len(sys.argv) > 2 else '',
        end_url=sys.argv[3] if len(sys.argv) > 3 else ''
    ).start()
# end if
