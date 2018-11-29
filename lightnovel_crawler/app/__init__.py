#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""
from PyInquirer import prompt
from .program import Program
from ..utils.crawler import Crawler


def check(crawler):
    return crawler.__bases__.count(Crawler) == 1
# end for


def get_novel_url():
    answer = prompt([
        {
            'type': 'input',
            'name': 'novel',
            'message': 'What is the url of novel page?',
            'validate': lambda val: 'Url should be not be empty'
            if len(val) == 0 else True,
        },
    ])
    return answer['novel'].strip()
# end def


def start_app(choice_list):
    print('\n⮕ Press \33[95mCtrl + C\33[0m to exit\n')

    novel_url = get_novel_url()

    not_recognized = True
    for home_url, crawler in choice_list.items():
        if novel_url.startswith(home_url):
            instance = crawler()
            instance.novel_url = novel_url
            instance.home_url = home_url.strip('/')
            Program().run(instance)
            not_recognized = False
            break
        # end if
    # end for

    if not_recognized:
        print()
        print('-' * 80)
        print('Sorry! I do not recognize this website yet.')
        print('My domain is limited to these sites only:')
        for url in sorted(choice_list.keys()):
            print(' -', url)
        # end for
        print()
        print('-' * 80)
        print('Request developers to add your site at:')
        print('  https://github.com/dipu-bd/lightnovel-crawler/issues')
        print()
    else:
        print('-' * 80, end='\n\n')
        print('Bye bye. Come back soon!')
    # end if
# end def
