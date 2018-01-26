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

home_url = 'https://lnmtl.com/'
login_url = 'https://lnmtl.com/auth/login/'
logout_url = 'https://lnmtl.com/auth/logout'
email = 'dipu@algomatrix.co'
password = 'twill1123'

def get_browser():
    executable_path = path.join('lib', 'chromedriver')
    return Browser('chrome',
                   headless=True,
                   incognito=True,
                   executable_path=executable_path)
# end def

def start():
    if login():
        crawl_pages(start_url)
        logout()
    else:
        print('Failed to login')
    # end with
# end def

def login():
    print('Attempting login:', login_url)
    browser.visit(login_url)
    browser.find_by_css('form input#email').fill(email)
    browser.find_by_css('form input#password').fill(password)
    browser.find_by_css('form button[type="submit"]').click()
    return browser.url == home_url
# end def

def logout():
    print('Attempting logout:', logout_url)
    browser.visit(logout_url)
    return browser.url == home_url
# end def

def crawl_pages(url):
    while url:
        print('Visiting:', url)
        browser.visit(url)
        # parse contents
        titles = browser.find_by_css('div.dashhead-titles')
        novel = titles.find_by_css('.dashhead-subtitle a')[0]['title']
        volume = titles.find_by_css('.dashhead-subtitle').first.text
        chapter = titles.find_by_css('.dashhead-title').first.text
        translated = browser.find_by_css('.chapter-body .translated')
        # format contents
        chapter = format_text(chapter)
        body = ''.join([format_text(x.text) for x in translated if x.text.strip()])
        volume_no = re.search(r'\d+$', volume).group()
        chapter_no = re.search(r'\d+$', url).group()
        content = {
            'url': url,
            'novel': novel.strip(),
            'volume_no': volume_no,
            'chapter_no': chapter_no,
            'chapter_title': chapter,
            'body': '<h1>%s</h1>%s' % (chapter, body)
        }
        # save data
        save_chapter(content)
        # move on to next
        if url.strip('/') == end_url.strip('/'): break
        url = browser.find_by_css('nav .pager .next a').first['href']
    # end while
# end def

def format_text(text):
    text = text.replace(u'\u00ad', '')
    text = re.sub(r'\u201e[, ]*', '&ldquo;', text)
    text = re.sub(r'\u201d[, ]*', '&rdquo;', text)
    # text = re.sub(r'[^\x00-\x7f]', r'', text)
    return '<p>' + text.strip() + '</p>'
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
    start_url = sys.argv[2]
    end_url = sys.argv[3] if len(sys.argv) > 3 else ''
    output_path = path.join('_novel', novel_id)

    browser = get_browser()
    try:
        start()
    finally:
        browser.quit()
    # end try

    novel_to_kindle(output_path)
# end if
