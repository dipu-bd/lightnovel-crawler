# -*- coding: utf-8 -*-
import os
import textwrap

from colorama import Back, Fore, Style

from ..assets.icons import Icons

LINE_SIZE = 80
ENABLE_BANNER = not Icons.isWindows

try:
    row, _ = os.get_terminal_size()
    if row < LINE_SIZE:
        LINE_SIZE = row
    # end if
except Exception:
    pass
# end try


def description():
    print('=' * LINE_SIZE)

    if ENABLE_BANNER:
        from ..assets.banner import get_color_banner
        print(get_color_banner())
    else:
        from ..assets.version import get_version
        title = Icons.BOOK + ' Lightnovel Crawler v' + get_version()
        padding = ' ' * ((LINE_SIZE - len(title)) // 2)
        print(Fore.YELLOW, padding + title, Fore.RESET)
        desc = 'https://github.com/dipu-bd/lightnovel-crawler'
        padding = ' ' * ((LINE_SIZE - len(desc)) // 2)
        print(Fore.CYAN, padding + desc, Fore.RESET)
    # end if

    print('-' * LINE_SIZE)
# end def


def epilog():
    print()
    print('-' * LINE_SIZE)

    # print(' ' + Icons.HANDS, Fore.CYAN,
    #       'https://discord.gg/7A5Hktx', Fore.RESET)

    print(' ' + Icons.LINK, Fore.CYAN,
          'https://github.com/dipu-bd/lightnovel-crawler/issues', Fore.RESET)

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

    print(' ', Icons.RIGHT_ARROW, Style.DIM + 'Upgrade using',
          Fore.YELLOW + 'pip install -U lightnovel-crawler', Style.RESET_ALL)

    # if Icons.isWindows:
    #     print('', Icons.RIGHT_ARROW, Style.DIM + 'Download:',
    #           Fore.YELLOW + 'https://rebrand.ly/lncrawl', Style.RESET_ALL)
    # elif Icons.isLinux:
    #     print('', Icons.RIGHT_ARROW, Style.DIM + 'Download:',
    #           Fore.YELLOW + 'https://rebrand.ly/lncrawl-linux', Style.RESET_ALL)
    # # end if

    print('-' * LINE_SIZE)
# end def


def url_supported_list():
    from .sources import crawler_list
    print('List of %d supported sources:' % len(crawler_list))
    for url in sorted(crawler_list.keys()):
        print(Fore.LIGHTGREEN_EX, Icons.RIGHT_ARROW, url, Fore.RESET)
    # end for
# end def


def url_not_recognized():
    print()
    print(Fore.RED, Icons.ERROR,
          'Sorry! I do not recognize this website yet.', Fore.RESET)
    print()
    print('Find the list of supported/rejected sources here:')
    print(Fore.CYAN, Icons.LINK,
          'https://github.com/dipu-bd/lightnovel-crawler#supported-sources', Fore.RESET)
    print()
    # print('You can request developers to add support for this site here:')
    # print(Fore.CYAN, Icons.LINK,
    #       'https://github.com/dipu-bd/lightnovel-crawler/issues', Fore.RESET)
# end def


def url_rejected(reason):
    print()
    print(Fore.RED, Icons.ERROR, 'Sorry! I do not support this website.', Fore.RESET)
    print(Fore.RED, Icons.EMPTY, 'Reason:', reason, Fore.RESET)
    print()
    print('-' * LINE_SIZE)
    print('You can try other available sources or create an issue if you find something\nhas went wrong:')
    print(Fore.CYAN, Icons.LINK,
          'https://github.com/dipu-bd/lightnovel-crawler/issues', Fore.RESET)
# end def


def format_short_info_of_novel(short_info):
    if not short_info or len(short_info) == 0:
        return ''
    # end if
    return '\n'.join(textwrap.wrap(
        short_info.strip(),
        width=70,
        initial_indent='\n' + (' ' * 6) + Icons.INFO + ' ',
        subsequent_indent=(' ' * 8),
        drop_whitespace=True,
        break_long_words=True,
    ))
# end def


def format_novel_choices(choices):
    items = []
    for index, item in enumerate(choices):
        text = '%d. %s [in %d sources]' % (index + 1, item['title'], len(item['novels']))
        if len(item['novels']) == 1:
            novel = item['novels'][0]
            text += '\n' + (' ' * 6) + Icons.LINK + ' ' + novel['url']
            text += format_short_info_of_novel(novel.get('info', ''))
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


def format_resume_choices(metadata_list):
    items = []
    for index, data in enumerate(metadata_list):
        if not data.get('session'):
            continue
        text = '%d. %s [downloading %d chapters]' % (
            index + 1,
            data['title'],
            len(data['session']['download_chapters'])
        )
        text += '\n' + (' ' * 6) + Icons.LINK + ' ' + data['url']
        items.append({'name': text})
    # end for
    return items
# end def
