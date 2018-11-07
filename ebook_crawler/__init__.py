#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive value input"""
from PyInquirer import prompt
from .lnmtl import LNMTLCrawlerApp
# from .wuxia import WuxiaCrawler
# from .wuxiac import WuxiaCoCrawler
# from .webnovel import WebNovelCrawler
# from .boxnovel import BoxNovelCrawler
# from .readln import ReadLightNovelCrawler
# from .novelplanet import NovelPlanetCrawler

def main():
    questions = [
        {
            'type': 'list',
            'name': 'source',
            'message': 'Where is your novel from?',
            'choices': [
                'https://lnmtl.com',
                'https://boxnovel.com',
                'https://novelplanet.com',
                'https://www.webnovel.com',
                'https://www.wuxiaworld.co',
                'https://www.wuxiaworld.com',
                'https://www.readlightnovel.org'
            ]
        },
    ]

    with open('VERSION', 'r') as f:
        version = f.read().strip()
    # end with
    print('-' * 60)
    print(' \33[1m\033[92m🍀', 'Ebook Crawler', version, '\33[0m')
    print(' 🔗\033[94m https://github.com/dipu-bd/site-to-epub', '\033[0m')
    print(' 🙏\033[94m https://saythanks.io/to/dipu-bd', '\033[0m')
    print('-' * 60)

    answer = prompt(questions)
    if 'https://lnmtl.com' == answer['source']:
        LNMTLCrawlerApp().start()
    elif 'https://boxnovel.com' == answer['source']:
        print('Not Yet Implemented: ', answer['source'])
    elif 'https://novelplanet.com' == answer['source']:
        print('Not Yet Implemented: ', answer['source'])
    elif 'https://www.webnovel.com' == answer['source']:
        print('Not Yet Implemented: ', answer['source'])
    elif 'https://www.wuxiaworld.co' == answer['source']:
        print('Not Yet Implemented: ', answer['source'])
    elif 'https://www.wuxiaworld.com' == answer['source']:
        print('Not Yet Implemented: ', answer['source'])
    elif 'https://www.readlightnovel.org' == answer['source']:
        print('Not Yet Implemented: ', answer['source'])
    # end if
# end def

if __name__ == '__main__':
    main()
# end if
