import os
import textwrap

from colorama import Back, Fore, Style

from .icons import Icons

LINE_SIZE = 64


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
    levels = ['', 'WARN', 'INFO', 'DEBUG']

    text = Fore.RED + ' ' + Icons.SOUND + ' '
    text += 'LOG LEVEL = %s' % levels[level]
    text += Fore.RESET

    padding = ' ' * ((LINE_SIZE - len(text)) // 2)
    print(padding + text)

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


def url_not_recognized(choice_list):
    print()
    print('-' * LINE_SIZE)
    print('Sorry! I do not recognize this website yet.')
    print('My domain is limited to these sites only:')
    for url in sorted(choice_list.keys()):
        print(Fore.LIGHTGREEN_EX, Icons.RIGHT_ARROW, url, Fore.RESET)
    # end for
    print()
    print('-' * LINE_SIZE)
    print('Request developers to add your site at:')
    print(Fore.CYAN, Icons.LINK,
          'https://github.com/dipu-bd/lightnovel-crawler/issues', Fore.RESET)
    print()
# end def
