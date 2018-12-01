#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive value input"""
import os
import sys
import logging
import platform
import requests
from colorama import init as init_colorama, Fore, Back, Style

from .app import start_app, Icons

from .lnmtl import LNMTLCrawler
from .webnovel import WebnovelCrawler
from .wuxia import WuxiaCrawler
from .wuxiac import WuxiaCoCrawler
from .wuxiaonline import WuxiaOnlineCrawler
from .boxnovel import BoxNovelCrawler
from .readln import ReadLightNovelCrawler
from .novelplanet import NovelPlanetCrawler
from .lnindo import LnindoCrawler
from .idqidian import IdqidianCrawler
from .utils.crawler import Crawler

crawler_list = {
    'https://lnmtl.com/': LNMTLCrawler,
    'https://www.webnovel.com/': WebnovelCrawler,
    'https://wuxiaworld.online/': WuxiaOnlineCrawler,
    'https://www.wuxiaworld.com/': WuxiaCrawler,
    'https://www.wuxiaworld.co/': WuxiaCoCrawler,
    'https://boxnovel.com/': BoxNovelCrawler,
    'https://novelplanet.com/': NovelPlanetCrawler,
    'https://www.readlightnovel.org/': ReadLightNovelCrawler,
    'https://lnindo.org/': LnindoCrawler,
    'https://www.idqidian.us/': IdqidianCrawler,
}


dir_name = os.path.dirname(__file__)
with open(os.path.join(dir_name, '..', 'VERSION'), 'r') as f:
    __version__ = f.read().strip()
# end with


def configure():
    init_colorama()
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else None

    if mode == '-v' or mode == '--verbose':
        os.environ['debug_mode'] = 'true'
        print(Fore.RED, Icons.SOUND, 'IN VERBOSE MODE', Fore.RESET)
        print('-' * 60)
        logging.basicConfig(level=logging.DEBUG)
    # end if
    requests.urllib3.disable_warnings(
        requests.urllib3.exceptions.InsecureRequestWarning)
    # end if
# end def


def headline():
    print('-' * 60)
    print(Fore.GREEN, Icons.BOOK + 'Ebook Crawler', Icons.CLOVER + __version__, Fore.RESET)
    print(Icons.LINK, Fore.CYAN + 'https://github.com/dipu-bd/site-to-epub' + Fore.RESET)
    print(Icons.HANDS, Fore.CYAN + 'https://saythanks.io/to/dipu-bd' + Fore.RESET)
    print('-' * 60)
# end def


def main():
    configure()

    headline()
    start_app(crawler_list)
# end def


if __name__ == '__main__':
    main()
# end if
