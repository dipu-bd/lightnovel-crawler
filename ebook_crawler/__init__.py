#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive value input"""
import sys
import logging
import requests

from .app import start_app

from .lnmtl import LNMTLCrawler
from .webnovel import WebnovelCrawler
from .wuxia import WuxiaCrawler
from .wuxiac import WuxiaCoCrawler
from .boxnovel import BoxNovelCrawler
from .readln import ReadLightNovelCrawler
from .novelplanet import NovelPlanetCrawler
from .lnindo import LnindoCrawler
from .idqidian import IdqidianCrawler
from .utils.crawler import Crawler


crawler_list = {
    'https://lnmtl.com': LNMTLCrawler,
    'https://www.webnovel.com': WebnovelCrawler,
    'https://www.wuxiaworld.com': WuxiaCrawler,
    'https://www.wuxiaworld.co': WuxiaCoCrawler,
    'https://boxnovel.com': BoxNovelCrawler,
    'https://novelplanet.com': NovelPlanetCrawler,
    'https://www.readlightnovel.org': ReadLightNovelCrawler,
    'https://lnindo.org': LnindoCrawler,
    'https://www.idqidian.us': IdqidianCrawler,
}

def configure():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else None
    if mode == '-v' or mode == '--verbose':
        print('\33[91m 🔊 IN VERBOSE MODE\33[0m')
        print('-' * 60)
        logging.basicConfig(level=logging.DEBUG)
    # end if
    requests.urllib3.disable_warnings(
        requests.urllib3.exceptions.InsecureRequestWarning)
    # end if
# end def

def headline():
    with open('VERSION', 'r') as f:
        version = f.read().strip()
    # end with
    print('\033c', end='')
    print('-' * 60)
    print(' \33[1m\33[92m📒', 'Ebook Crawler 🍀', version, '\33[0m')
    print(' 🔗\33[94m https://github.com/dipu-bd/site-to-epub', '\33[0m')
    print(' 🙏\33[94m https://saythanks.io/to/dipu-bd', '\33[0m')
    print('-' * 60)
# end def

def main():
    headline()
    configure()

    start_app(crawler_list)
# end def

if __name__ == '__main__':
    main()
# end if
