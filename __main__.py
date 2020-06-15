#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lncrawl.app.config import CONFIG
from lncrawl.app.models import *
from lncrawl.app.browser import *

print(CONFIG.get('browser/parser/cloudscraper'))
print(CONFIG.get('logging/version'))
print(CONFIG.get('logging/loggers/level'))
print()

print(Language.ENGLISH)
print(Author('Sudipto Chandra', AuthorType.AUTHOR))
print(Chapter(Volume(Novel('http://www.google.com'), 2), 10))
print()

b = Browser()
duck = b.get('https://duckduckgo.com/')
print(duck)
print(duck.soup.select_one('link[rel="canonical"]')['href'])
print()

ab = AsyncBrowser()
for i in range(2):
    novel = ab.get('https://api.duckduckgo.com/?q=novel&format=json')
    anything = ab.get('https://api.duckduckgo.com/?q=anything&format=json')
    print(novel.result().json['AbstractURL'])
    print(anything.result().json['AbstractURL'])
print()
