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

novel_name = 'Unknown'


def get_browser():
    executable_path = path.join('lib', 'chromedriver')
    return Browser('chrome',
                   headless=True,
                   incognito=True,
                   executable_path=executable_path)
# end def

def start():
    try:
        meta_info()
        crawl_pages(start_url)
    finally:
        browser.quit()
    # end try
# end def

def meta_info():
    global novel_name
    print('Visiting:', home_url)
    browser.visit(home_url)
    novel_name = browser.find_by_css('h1.entry-title').first.text
    novel_name = re.sub(r' – Index$', '', novel_name)
# end def

def crawl_pages(url):
    while url:
        print('Visiting:', url)
        browser.visit(url)
        next_link = browser.find_link_by_partial_text('Next Chapter')
        if not next_link: break
        # parse contents
        chapter_no = re.search(r'\d+.?$', url).group().strip('/')
        vol_no = str(1 + int(chapter_no) // 100)
        if re.match(r'.*-book-\d+-chapter-\d+', url):
            vol_no = re.search(r'-\d+-', url).group().strip('-')
        # end if
        articles = browser.find_by_css('div[itemprop="articleBody"] p')
        chapter_title = articles[1].text
        if re.match(r'Chapter \d+.*', articles[2].text):
            chapter_title = articles[2].text
        # end if
        body = [x for i, x in enumerate(articles) if 0 < i < len(articles) - 1]
        body = '\n'.join(['<p>' + x.html + '</p>' for x in body])
        # save data
        save_chapter({
            'url': url,
            'novel': novel_name,
            'chapter_no': chapter_no,
            'chapter_title': chapter_title,
            'volume_no': vol_no,
            'body': body
        })
        # move on to next
        if url == end_url: break
        url = next_link.first['href'].strip('/')
    # end while
# end def

def save_chapter(content):
    # save to file
    vol = content['volume_no'].rjust(2, '0')
    chap = content['chapter_no'].rjust(5, '0')
    file_name = path.join(output_path, vol, chap + '.json')
    if not path.exists(path.dirname(file_name)):
        makedirs(path.dirname(file_name))
    # end if
    with open(file_name, 'w') as file:
        file.write(json.dumps(content))
    # end with
# end def

if __name__ == '__main__':
    novel_id = sys.argv[1]
    start_url = sys.argv[2].strip('/')
    end_url = sys.argv[3].strip('/') if len(sys.argv) > 3 else ''

    output_path = path.join('_novel', novel_id)
    home_url = 'http://www.wuxiaworld.com/%s-index' % (novel_id)
    if start_url.isdigit():
        start_url = '%s/%s-chapter-%s' % (home_url, novel_id, start_url)
    # end if
    if end_url.isdigit():
        end_url = '%s/%s-chapter-%s' % (home_url, novel_id, end_url)
    # end if

    # browser = get_browser()
    # start()
    novel_to_kindle(output_path)
# end if
