#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive value input"""
import sys
import logging
import requests
from PyInquirer import prompt
from .app import run_app
from .lnmtl import LNMTLCrawler
from .webnovel import WebnovelCrawler
from .wuxia import WuxiaCrawler
# from .wuxiac import WuxiaCoCrawler
# from .boxnovel import BoxNovelCrawler
# from .readln import ReadLightNovelCrawler
# from .novelplanet import NovelPlanetCrawler

def configure():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else None
    if mode == '-v' or mode == '--verbose':
        print('\33[91m 🔊 IN VERBOSE MODE\33[0m')
        print('-' * 60)
        logging.basicConfig(level=logging.DEBUG)
    else:
        requests.urllib3.disable_warnings(
            requests.urllib3.exceptions.InsecureRequestWarning)
    # end if
# end def

def headline():
    with open('VERSION', 'r') as f:
        version = f.read().strip()
    # end with
    print('-' * 60)
    print(' \33[1m\33[92m📒', 'Ebook Crawler 🍀', version, '\33[0m')
    print(' 🔗\33[94m https://github.com/dipu-bd/site-to-epub', '\33[0m')
    print(' 🙏\33[94m https://saythanks.io/to/dipu-bd', '\33[0m')
    print('-' * 60)
# end def

def get_choice():
    not_implemented = lambda: print('\n  Not yet implemented  \n') or None

    choices = {
        'https://lnmtl.com': LNMTLCrawler,
        'https://www.webnovel.com': WebnovelCrawler,
        'https://www.wuxiaworld.com': WuxiaCrawler,
        'https://www.readlightnovel.org': not_implemented,
        'https://novelplanet.com': not_implemented,
        'https://www.wuxiaworld.co': not_implemented,
        'https://boxnovel.com': not_implemented,
    }

    answer = prompt([
        {
            'type': 'list',
            'name': 'source',
            'message': 'Where is the novel from?',
            'choices': choices.keys(),
        },
    ])

    return choices[answer['source']]()
# end def

def main():
    headline()
    configure()

    error = False
    while True:
        try:
            crawler = get_choice()
            run_app(crawler)
            error = False
        except:
            if error:
                break
            else:
                error = True
                print('\n⮕ Press \33[95mCtrl + C\33[0m again to exit\n')
            # end if
        # end try
    # end if
# end def

if __name__ == '__main__':
    main()
# end if
