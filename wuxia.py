#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawler LNMTL novels and create epub files

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.
"""
import sys
from os import path, makedirs
import re
import json
from splinter import Browser
from binding import novel_to_kindle


def get_browser():
    '''open a headless chrome browser in incognito mode'''
    executable_path = path.join('lib', 'chromedriver')
    return Browser('chrome',
                   headless=True,
                   incognito=True,
                   executable_path=executable_path)
# end def


class WuxiaCrawler:
    '''Crawler for WuxiaWorld'''

    def __init__(self, novel_id, start_url=None, end_url=None):
        if not novel_id:
            raise Exception('Novel ID is required')
        # end if

        self.novel_id = novel_id
        self.novel_name = 'Unknown'
        self.author_name = 'Sudipto Chandra'

        self.home_url = 'http://www.wuxiaworld.com/%s-index' % (novel_id)
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
            return '%s/%s-chapter-%s' % (self.home_url, self.novel_id, chapter)
        else:
            return chapter.strip('/')
    # end def

    def start(self):
        '''start crawling'''
        browser = get_browser()
        try:
            if self.start_url:
                self.crawl_meta_info(browser)
                self.crawl_chapters(browser)
            # end if
        finally:
            browser.quit()
        # end try
        novel_to_kindle(self.output_path)
    # end def

    def crawl_meta_info(self, browser):
        '''get novel name and author'''
        print('Visiting:', self.home_url)
        browser.visit(self.home_url)
        novel = browser.find_by_css('h1.entry-title').first.text
        self.novel_name = re.sub(r' – Index$', '', novel)
    # end def

    def crawl_chapters(self, browser):
        '''Crawl all chapters till the end'''
        url = self.start_url
        while url:
            print('Visiting:', url)
            browser.visit(url)
            next_link = browser.find_link_by_partial_text('Next Chapter')
            if not next_link:
                break
            # end if
            self.parse_chapter(browser)
            if url == self.end_url:
                break
            # end if
            url = next_link.first['href'].strip('/')
        # end while
    # end def

    def parse_chapter(self, browser):
        '''Parse the content of the chapter page'''
        url = browser.url.strip('/')
        chapter_no = re.search(r'\d+.?$', url).group().strip('/')
        vol_no = str(1 + (int(chapter_no) - 1) // 100)
        if re.match(r'.*-book-\d+-chapter-\d+', url):
            vol_no = re.search(r'-\d+-', url).group().strip('-')
        # end if
        articles = browser.find_by_css('div[itemprop="articleBody"] p')
        body = [x for x in articles][1:-1]
        chapter_title = body[0].text
        if re.match(r'Chapter \d+.*', body[1].text):
            chapter_title = body[1].text
            body = body[2:]
        else:
            body = body[1:]
        # end if
        body = ''.join(['<p>' + x.html + '</p>' for x in body if x.text.strip()])
        # save data
        self.save_chapter({
            'url': url,
            'novel': self.novel_name,
            'chapter_no': chapter_no,
            'chapter_title': chapter_title,
            'volume_no': vol_no,
            'body': '<h1>%s</h1>%s' % (chapter_title, body)
        })
    # end def

    def save_chapter(self, content):
        '''save content to file'''
        vol = content['volume_no'].rjust(2, '0')
        chap = content['chapter_no'].rjust(5, '0')
        file_name = path.join(self.output_path, vol, chap + '.json')
        if not path.exists(path.dirname(file_name)):
            makedirs(path.dirname(file_name))
        # end if
        print('Saving ', file_name)
        with open(file_name, 'w') as file:
            file.write(json.dumps(content))
        # end with
    # end def
# end class

if __name__ == '__main__':
    WuxiaCrawler(
        novel_id=sys.argv[1],
        start_url=sys.argv[2] if len(sys.argv) > 2 else None,
        end_url=sys.argv[3] if len(sys.argv) > 3 else None
    ).start()
# end if
