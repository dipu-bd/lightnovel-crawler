#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crawler LNMTL novels and create epub files

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.

Requirements:
> Selenium: conda install -c conda-forge selenium
> Splinter: conda install -c metaperl splinter
> Pypub: pip install pypub
> Chrome Driver: https://sites.google.com/a/chromium.org/chromedriver/downloads
> Make `chromedriver` accessible via terminal
> KindleGen: https://www.amazon.com/gp/feature.html?docId=1000765211
> Make `kindlegen` accessible via terminal
"""
from os import path, makedirs, listdir
from subprocess import call
import re
import json
import pypub
from splinter import Browser
from lnmtl_settings import *


def start():
    if login():
        crawl_pages(start_url)
        logout()
    else:
        print('Failed to login')
    # end with
# end def

def login():
    print('Attempting login: ' + login_url)
    browser.visit(login_url)
    browser.find_by_css('form input#email').fill(email)
    browser.find_by_css('form input#password').fill(password)
    browser.find_by_css('form button[type="submit"]').click()
    return browser.url == home_url
# end def

def logout():
    print('Attempting logout: ' + logout_url)
    browser.visit(logout_url)
    return browser.url == home_url
# end def

def crawl_pages(url):
    # visit url
    print('Visiting:' + url)
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
    file_name = path.join(crawl_output, vol, chap + '.json')
    if not path.exists(path.dirname(file_name)):
        makedirs(path.dirname(file_name))
    # end if
    with open(file_name, 'w') as file:
        file.write(json.dumps(content))
    # end with
# end def

def convert_to_epub():
    for vol in sorted(listdir(crawl_output)):
        data = []
        full_vol = path.join(crawl_output, vol)
        print('Processing: ' + full_vol)
        for file in sorted(listdir(full_vol)):
            full_file = path.join(full_vol, file)
            f = open(full_file, 'r')
            data.append(json.load(f))
            f.close()
        # end for
        data.sort(key=lambda x: x['chapter_no'])
        create_epub(vol, data)
    # end for
# end def

def create_epub(volume_no, data):
    vol = str(volume_no).rjust(2, '0')
    title = epub_title + ' Volume ' + vol
    print('Creating EPUB:' + title)
    epub = pypub.Epub(title, 'Sudipto Chandra')
    for item in data:
        title = (item['chapter_title'] or '....')
        html = '<?xml version="1.0" encoding="UTF-8" ?>\n'\
            + '<!DOCTYPE html>'\
            + '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">'\
            + '<head>'\
            + '<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />'\
            + '<title>' + item['volume_title'] + '</title>'\
            + '</head>'\
            + '<body style="text-align: justify">'\
            + '<h1>' + title + '</h1>'\
            + '\n'.join([ '<p>' + x + '</p>' for x in item['body']])\
            + '</body>'\
            + '</html>'
        chapter = pypub.Chapter(content=html, title=title)
        epub.add_chapter(chapter)
    # end for
    if not path.exists(epub_output):
        makedirs(epub_output)
    # end if
    epub.create_epub(epub_output)
# def

def convert_to_mobi():
    for file_name in listdir(epub_output):
        if not file_name.endswith('.epub'):
            continue
        # end if
        input_file = path.join(epub_output, file_name)
        call(['kindlegen', path.abspath(input_file)])
    # end for
# end def

if __name__ == '__main__':
    browser = Browser('chrome')
    start()
    browser.quit()
    convert_to_epub()
    convert_to_mobi()
# end if
