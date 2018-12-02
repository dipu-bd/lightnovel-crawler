#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive value input"""
import os
import logging
import requests
from colorama import init as init_colorama
from .app import start_app
from .app.arguments import get_args, build_parser
from .app.display import description, epilog, debug_mode

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


def main():
    init_colorama()

    cur_dir = os.path.dirname(__file__)
    ver_file = os.path.join(cur_dir, '..', 'VERSION')
    with open(ver_file, 'r') as f:
        os.environ['version'] = f.read().strip()
    # end with

    description()
    build_parser()

    args = get_args()
    if args.log:
        os.environ['debug_mode'] = 'true'
        levels = [None, logging.WARN, logging.INFO, logging.DEBUG]
        logging.basicConfig(level=levels[args.log])
        debug_mode(args.log)
        print(args)
    # end if
    requests.urllib3.disable_warnings(
        requests.urllib3.exceptions.InsecureRequestWarning)
    # end if

    try:
        start_app(crawler_list)
    except Exception as err:
        if args.log == 3:
            raise err
        # end if
    # end try

    epilog()
# end def


if __name__ == '__main__':
    main()
# end if
