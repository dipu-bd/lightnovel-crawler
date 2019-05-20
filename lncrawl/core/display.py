#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import textwrap
from urllib.parse import urlparse

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

    desc = 'https://github.com/dipu-bd/lightnovel-crawler'
    padding = ' ' * ((LINE_SIZE - len(desc)) // 2)
    print(Style.DIM, padding + desc, Style.RESET_ALL)

    print('-' * LINE_SIZE)
# end def


def epilog():
    print()
    print('-' * LINE_SIZE)

    print(' ' + Icons.LINK, Fore.CYAN,
          'https://github.com/dipu-bd/lightnovel-crawler/issues', Fore.RESET)

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
    print(Style.BRIGHT + Fore.YELLOW + Icons.SPARKLE,
          'Task completed', Fore.RESET, Style.RESET_ALL)
    print()
# end def


def new_version_news(latest):
    print('', Icons.PARTY + Style.BRIGHT + Fore.CYAN,
          'VERSION', Fore.RED + latest + Fore.CYAN,
          'IS NOW AVAILABLE!', Fore.RESET)

    print('', Icons.RIGHT_ARROW, Style.DIM + 'Upgrade:',
          Fore.YELLOW + 'pip install -U lightnovel-crawler', Style.RESET_ALL)

    if Icons.isWindows:
        print('', Icons.RIGHT_ARROW, Style.DIM + 'Download EXE:',
              Fore.YELLOW + 'http://bit.ly/2I1XzeN', Style.RESET_ALL)
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


def format_short_info_of_novel(short_info):
    if not short_info or len(short_info) == 0:
        return ''
    # end if
    return '\n'.join(textwrap.wrap(
        short_info,
        width=70,
        initial_indent='\n' + (' ' * 6) + Icons.INFO,
        subsequent_indent=(' ' * 8),
        drop_whitespace=True,
        break_long_words=True,
    ))
# end def


def format_novel_choices(choices):
    items = []
    for index, item in enumerate(choices):
        text = '%d. %s [in %d sources]' % (
            index + 1, item['title'], len(item['novels']))
        if len(item['novels']) == 1:
            novel = item['novels'][0]
            short_info = novel['info'] if 'info' in novel else ''
            text += '\n' + (' ' * 6) + '- ' + novel['url']
            text += format_short_info_of_novel(short_info)
        # end if
        items.append({'name': text})
    # end for
    return items
# end def


def format_source_choices(novels):
    items = []
    for index, item in enumerate(novels):
        text = '%d. %s' % (index + 1, item['url'])
        short_info = item['info'] if 'info' in item else ''
        text += format_short_info_of_novel(short_info)
        items.append({'name': text})
    # end for
    return items
# end def
