#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""
import platform
from colorama import Fore
from PyInquirer import prompt
from .program import Program
from ..utils.crawler import Crawler


class Icons:
    windows = platform.system() != 'Windows'
    BOOK = '📒 ' if windows else ''
    CLOVER = '🍀 ' if windows else '#'
    LINK = ' 🔗' if windows else ' -'
    HANDS = ' 🙏' if windows else ' -'
    SOUND = '🔊' if windows else '>>'
    RIGHT_ARROW = '⮕' if windows else '->'
# end def


def check(crawler):
    return crawler.__bases__.count(Crawler) == 1
# end for


def get_novel_url():
    answer = prompt([
        {
            'type': 'input',
            'name': 'novel',
            'message': 'What is the url of novel page?',
            'validate':  lambda val: 'Url should be not be empty' \
                if len(val) == 0 else True,
        },
    ])
    return answer['novel'].strip()
# end def


def start_app(choice_list):
    print()
    print(Icons.RIGHT_ARROW, 'Press', Fore.MAGENTA, 'Ctrl + C', Fore.RESET, 'to exit')
    print()

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
            print(Fore.LIGHTGREEN_EX, Icons.RIGHT_ARROW, url, Fore.RESET)
        # end for
        print()
        print('-' * 80)
        print('Request developers to add your site at:')
        print(Fore.CYAN, Icons.LINK, 'https://github.com/dipu-bd/lightnovel-crawler/issues', Fore.RESET)
        print()
    else:
        print('-' * 80, end='\n\n')
        print('Bye bye. Come back soon!')
    # end if
# end def
