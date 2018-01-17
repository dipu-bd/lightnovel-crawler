#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawler LNMTL novels and create epub files

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.
"""
from os import path, makedirs
import re
import json
from splinter import Browser
from lnmtl_settings import *
from binding import *


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
    # visit url
    print('Visiting:', url)
    if not url: return
    browser.visit(url)
    # get contents
    titles = browser.find_by_css('div.dashhead-titles')
    novel = titles.find_by_css('.dashhead-subtitle a')[0]['title']
    volume = titles.find_by_css('.dashhead-subtitle').first.text
    chapter = titles.find_by_css('.dashhead-title').first.text
    translated = browser.find_by_css('.chapter-body .translated')
    body = [ sentence.text for sentence in translated ]
    # format contents
    volume_no = re.search(r'\d+$', volume).group()
    chapter_no = re.search(r'\d+$', url).group()
    content = {
        'url': url,
        'novel': novel.strip(),
        'volume_no': int(volume_no),
        'chapter_no': int(chapter_no),
        'volume_title': volume.strip(),
        'chapter_title': re.sub(r'[^\x00-\x7f]', r'', chapter).strip(),
        'body': [ re.sub(r'[^\x00-\x7f]', r'', x).strip() for x in body if x ]
    }
    # save data
    save_chapter(content)
    # move on to next
    if url.strip('/') == end_url.strip('/'): return
    crawl_pages(browser.find_by_css('nav .pager .next a').first['href'])
# end def

def save_chapter(content):
    # save to file
    vol = str(content['volume_no'])
    chap = str(content['chapter_no'])
    file_name = path.join('_data', novel_id, vol, chap + '.json')
    if not path.exists(path.dirname(file_name)):
        makedirs(path.dirname(file_name))
    # end if
    with open(file_name, 'w') as file:
        file.write(json.dumps(content))
    # end with
# end def

if __name__ == '__main__':
    browser = Browser('chrome', incognito=True)
    start()
    browser.quit()
    convert_to_epub(novel_id)
    convert_to_mobi(novel_id)
# end if
