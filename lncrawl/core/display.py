import os
import textwrap
import traceback
from typing import List

from colorama import Fore, Style

from ..assets.chars import Chars
from ..utils.platforms import Platform
from ..core.exeptions import LNException
from ..models import CombinedSearchResult, SearchResult
from ..models.meta import MetaInfo

LINE_SIZE = 80
ENABLE_BANNER = not Platform.windows or Platform.java

try:
    row, _ = os.get_terminal_size()
    if row < LINE_SIZE:
        LINE_SIZE = row

except Exception:
    pass


def description():
    print("=" * LINE_SIZE)

    if ENABLE_BANNER:
        from ..assets.banner import get_color_banner

        print(get_color_banner())
    else:
        from ..assets.version import get_version

        title = Chars.BOOK + " Lightnovel Crawler v" + get_version()
        padding = " " * ((LINE_SIZE - len(title)) // 2)
        print(Fore.YELLOW, padding + title, Fore.RESET)
        desc = "https://github.com/dipu-bd/lightnovel-crawler"
        padding = " " * ((LINE_SIZE - len(desc)) // 2)
        print(Fore.CYAN, padding + desc, Fore.RESET)

    print("-" * LINE_SIZE)


def epilog():
    print()
    print("-" * LINE_SIZE)

    # print(' ' + Chars.HANDS, Fore.CYAN,
    #       'https://discord.gg/7A5Hktx', Fore.RESET)

    print(
        " " + Chars.LINK,
        Fore.CYAN,
        "https://github.com/dipu-bd/lightnovel-crawler/issues",
        Fore.RESET,
    )

    print("=" * LINE_SIZE)


def debug_mode(level):
    text = Fore.RED + " " + Chars.SOUND + " "
    text += "LOG LEVEL: %s" % level
    text += Fore.RESET

    padding = " " * ((LINE_SIZE - len(text)) // 2)
    print(padding + text)

    print("-" * LINE_SIZE)


def input_suppression():
    text = Fore.RED + " " + Chars.ERROR + " "
    text += "Input is suppressed"
    text += Fore.RESET

    print(text)
    print("-" * LINE_SIZE)


def cancel_method():
    print()
    print(Chars.RIGHT_ARROW, "Press", Fore.MAGENTA, "Ctrl + C", Fore.RESET, "to exit")
    print()


def error_message(ex_type, message, tb):
    print()
    tb_summary = "".join(traceback.format_tb(tb)[-4:]).strip()
    print(Fore.RED, Chars.ERROR, "Error:", message, Fore.RESET)
    if tb_summary and ex_type not in [LNException, KeyboardInterrupt]:
        print(Style.DIM + str(ex_type) + Style.RESET_ALL)
        print(Style.DIM + str(tb_summary) + Style.RESET_ALL)

    print()


def app_complete():
    print(
        Style.BRIGHT + Fore.YELLOW + Chars.SPARKLE,
        "Task completed",
        Fore.RESET,
        Style.RESET_ALL,
    )
    print()


def new_version_news(latest):
    print(
        "",
        Chars.PARTY + Style.BRIGHT + Fore.CYAN,
        "VERSION",
        Fore.RED + latest + Fore.CYAN,
        "IS NOW AVAILABLE!",
        Fore.RESET,
    )

    print(
        " ",
        Chars.RIGHT_ARROW,
        Style.DIM + "Upgrade using",
        Fore.YELLOW + "pip install -U lightnovel-crawler",
        Style.RESET_ALL,
    )

    # if Platform.windows:
    #     print('', Chars.RIGHT_ARROW, Style.DIM + 'Download:',
    #           Fore.YELLOW + 'https://rebrand.ly/lncrawl', Style.RESET_ALL)
    # elif Platform.linux:
    #     print('', Chars.RIGHT_ARROW, Style.DIM + 'Download:',
    #           Fore.YELLOW + 'https://rebrand.ly/lncrawl-linux', Style.RESET_ALL)
    #

    print("-" * LINE_SIZE)


def url_supported_list():
    from .sources import crawler_list

    print("List of %d supported sources:" % len(crawler_list))
    for url in sorted(crawler_list.keys()):
        print(Fore.LIGHTGREEN_EX, Chars.RIGHT_ARROW, url, Fore.RESET)


def url_not_recognized():
    print()
    print(
        Fore.RED, Chars.ERROR, "Sorry! I do not recognize this website yet.", Fore.RESET
    )
    print()
    print("Find the list of supported/rejected sources here:")
    print(
        Fore.CYAN,
        Chars.LINK,
        "https://github.com/dipu-bd/lightnovel-crawler#supported-sources",
        Fore.RESET,
    )
    print()
    # print('You can request developers to add support for this site here:')
    # print(Fore.CYAN, Chars.LINK,
    #       'https://github.com/dipu-bd/lightnovel-crawler/issues', Fore.RESET)


def url_rejected(reason):
    print()
    print(Fore.RED, Chars.ERROR, "Sorry! I do not support this website.", Fore.RESET)
    print(Fore.RED, Chars.EMPTY, "Reason:", reason, Fore.RESET)
    print()
    print("-" * LINE_SIZE)
    print(
        "You can try other available sources or create an issue if you find something\nhas went wrong:"
    )
    print(
        Fore.CYAN,
        Chars.LINK,
        "https://github.com/dipu-bd/lightnovel-crawler/issues",
        Fore.RESET,
    )


def __format_search_result_info(short_info):
    if not short_info or len(short_info) == 0:
        return ""
    return "\n".join(
        textwrap.wrap(
            short_info.strip(),
            width=LINE_SIZE - 10,
            initial_indent="\n" + (" " * 6) + Chars.INFO + " ",
            subsequent_indent=(" " * 8),
            drop_whitespace=True,
            break_long_words=True,
        )
    )


def format_novel_choices(choices: List[CombinedSearchResult]):
    items = []
    for index, item in enumerate(choices):
        text = "%d. %s [in %d sources]" % (
            index + 1,
            item.title,
            len(item.novels),
        )
        if len(item.novels) == 1:
            novel = item.novels[0]
            text += "\n" + (" " * 6) + Chars.LINK + " " + novel.url
            text += __format_search_result_info(novel.info)

        items.append({"name": text})

    return items


def format_source_choices(novels: List[SearchResult]):
    items = []
    for index, item in enumerate(novels):
        text = "%d. %s" % (index + 1, item.url)
        text += __format_search_result_info(item.info)
        items.append({"name": text})

    return items


def format_resume_choices(meta_list: List[MetaInfo]):
    items = []
    for index, meta in enumerate(meta_list):
        if not meta.session:
            continue
        text = "%d. %s [downloading %d chapters]" % (
            index + 1,
            meta.novel.title,
            len(meta.session.download_chapters),
        )
        text += "\n" + (" " * 6) + Chars.LINK + " " + meta["url"]
        items.append({"name": text})

    return items
