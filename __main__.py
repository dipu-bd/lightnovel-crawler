#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.DEBUG)

try:
    from lncrawl.app.scraper import sources
    print(sources.scraper_list)
    print(sources.scraper_list[0].base_urls)
    print(sources.get_scraper_by_url('https://lnmtl.com/novel/dragon-of-the-root'))
    print(sources.get_scraper_by_name('lnmtl'))
finally:
    print()

try:
    from lncrawl.app.config import CONFIG
    print(CONFIG.get('browser/parser/cloudscraper'))
    print(CONFIG.get('logging/version'))
    print(CONFIG.get('logging/loggers/level'))
finally:
    print()

try:
    from lncrawl.app.models import *
    print(Language.ENGLISH)
    print(Author('Sudipto Chandra', AuthorType.AUTHOR))
    print(Chapter(Volume(Novel('http://www.google.com'), 2), 10))
finally:
    print()

# try:
#     from lncrawl.app.browser import Browser
#     b = Browser()
#     duck = b.get('https://duckduckgo.com/')
#     print(duck)
#     print(duck.soup.select_value('link[rel="canonical"]', value_of='href'))
#     print(duck.soup.find_value('meta', {'name': 'viewport'}, value_of='content'))
# finally:
#     print()

# try:
#     from lncrawl.app.browser import AsyncBrowser
#     ab = AsyncBrowser()
#     novel = ab.get('https://api.duckduckgo.com/?q=novel&format=json')
#     anything = ab.get('https://api.duckduckgo.com/?q=anything&format=json')
#     print(novel.result().json['AbstractURL'])
#     print(anything.result().json['AbstractURL'])
# finally:
#     print()


try:
    from lncrawl.app.scraper import Context
    context = Context('https://lnmtl.com/novel/dragon-of-the-root')

    print(context)
    # print(context.scraper.login('dipu@gmail.com', 'password'))
    print(context.scraper.fetch_novel_info(context.toc_url))
finally:
    print()
