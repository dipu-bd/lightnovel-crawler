#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
import textwrap
from colorama import Back, Fore, Style

from ..assets.icons import Icons
from ..spiders import crawler_list

LINE_SIZE = 80
try:
    row, _ = os.get_terminal_size()
    if row < LINE_SIZE:
        LINE_SIZE = row
    # end if
except:
    pass
# end try


def description():
    print('=' * LINE_SIZE)

    title = Icons.BOOK + ' Lightnovel Crawler ' + \
        Icons.CLOVER + os.getenv('version')
    padding = ' ' * ((LINE_SIZE - len(title)) // 2)
    print(Fore.YELLOW, padding + title, Fore.RESET)

    desc = 'Download lightnovels into html, text, epub, mobi and json'
    padding = ' ' * ((LINE_SIZE - len(desc)) // 2)
    print(Style.DIM, padding + desc, Style.RESET_ALL)

    print('-' * LINE_SIZE)
# end def


def epilog():
    print()
    print('-' * LINE_SIZE)

    print(' ' + Icons.LINK, Fore.CYAN,
          'https://github.com/dipu-bd/lightnovel-crawler', Fore.RESET)

    print(' ' + Icons.HANDS, Fore.CYAN,
          'https://saythanks.io/to/dipu-bd', Fore.RESET)

    print('=' * LINE_SIZE)
# end def


def debug_mode(level):
    text = Fore.RED + ' ' + Icons.SOUND + ' '
    text += 'LOG LEVEL: %s' % level
    text += Fore.RESET

    padding = ' ' * ((LINE_SIZE - len(text)) // 2)
    print(padding + text)

    print('-' * LINE_SIZE)
# end def


def input_suppression():
    text = Fore.RED + ' ' + Icons.ERROR + ' '
    text += 'Input is suppressed'
    text += Fore.RESET

    print(text)
    print('-' * LINE_SIZE)
# end def


def cancel_method():
    print()
    print(Icons.RIGHT_ARROW, 'Press', Fore.MAGENTA,
          'Ctrl + C', Fore.RESET, 'to exit')
    print()
# end def


def error_message(err):
    print()
    print(Fore.RED, Icons.ERROR, 'Error:', err, Fore.RESET)
    print()
# end def


def app_complete():
    print(Style.BRIGHT + Fore.YELLOW, Icons.sparkle,
          'Completed the task.', Fore.RESET, Style.RESET_ALL)
    print()
# end def


def new_version_news(latest):
    print('', Icons.PARTY + Style.BRIGHT + Fore.CYAN,
          'VERSION', Fore.RED + latest + Fore.CYAN,
          'IS NOW AVAILABLE!', Fore.RESET)

    print('', Icons.RIGHT_ARROW, Style.DIM + 'To upgrade:',
          Fore.YELLOW + 'pip install -U lightnovel-crawler', Style.RESET_ALL)

    if Icons.isWindows:
        print('', Icons.RIGHT_ARROW, Style.DIM + 'To download:',
              Fore.YELLOW + 'https://goo.gl/sc4EZh', Style.RESET_ALL)
    # end if

    print('-' * LINE_SIZE)
# end def


def url_not_recognized():
    print()
    print('-' * LINE_SIZE)
    print('Sorry! I do not recognize this website yet.')
    print('My domain is limited to these sites only:')
    for url in sorted(crawler_list.keys()):
        print(Fore.LIGHTGREEN_EX, Icons.RIGHT_ARROW, url, Fore.RESET)
    # end for
    print()
    print('-' * LINE_SIZE)
    print('You can request developers to add support for this site here:')
    print(Fore.CYAN, Icons.LINK,
          'https://github.com/dipu-bd/lightnovel-crawler/issues', Fore.RESET)
# end def
