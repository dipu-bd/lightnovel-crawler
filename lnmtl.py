#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Creates an epub from LNMTL novel

[LNMTL](https://lnmtl.com) is a website containing machine translated
novels. This code will convert any given book from this site into epub.

Requirements:
> Selenium: conda install -c conda-forge selenium
> Splinter: conda install -c metaperl splinter
> Chrome Driver: https://sites.google.com/a/chromium.org/chromedriver/downloads
> Make `chromedriver` accessible via terminal
"""
from splinter import Browser

# Settings
home_url = 'https://lnmtl.com'
login_url = 'https://lnmtl.com/auth/login'
email = 'dipu@algomatrix.co'
password = 'twill1123'
start_url = 'https://lnmtl.com/chapter/a-thought-through-eternity-chapter-900'
end_url = 'https://lnmtl.com/chapter/a-thought-through-eternity-chapter-902'

def login():
    print('Attempting login: ', login_url)
    browser.visit(login_url)
    browser.find_by_css('form input#email').fill(email)
    browser.find_by_css('form input#password').fill(password)
    browser.find_by_css('form button[type="submit"]').click()
    return browser.url == home_url
# end def

def crawl_pages(url):
    print('Visiting: ', url)
    if not url: return
    browser.visit(url)

    titles = browser.find_by_css('div.dashhead-titles')
    save_chapter({
        novel: titles.find_by_css('.dashhead-subtitle a')[0]['title']
        volume: titles.find_by_css('.dashhead-subtitle').first.text
        chapter: titles.find_by_css('.dashhead-title').first.text
        body: titles.find_by_css('.chapter-body').first.text
    })

    if url == end_url: return
    crawl_pages(browser.find_by_css('.pager .next a')[0]['href'])
# end def

def save_chapter(data):
    print()
    print(novel, volume, chapter, len(body))
# end def

if __name__ == '__main__':
    browser = Browser('chrome')
    if login():
        crawl_pages(start_url)
    else:
        print('Failed to login')
    browser.quit()
# end if