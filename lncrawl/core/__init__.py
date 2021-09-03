# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""
import logging
import os
import sys

import colorama
import urllib3
from colorama import Fore

from ..assets.version import get_version
from ..bots import run_bot
from .arguments import get_args
from .display import (cancel_method, debug_mode, description, epilog,
                      error_message, input_suppression)
from .sources import load_sources

logger = logging.getLogger(__name__)


def init():
    os.environ['version'] = get_version()

    colorama.init(wrap=True)
    description()

    args = get_args()

    levels = ['NOTSET', 'WARN', 'INFO', 'DEBUG']
    level = os.getenv('LOG_LEVEL')
    if not level:
        level = levels[args.log] if args.log else 'NOTSET'
        urllib3.disable_warnings()
    # end if
    if level != 'NOTSET':
        os.environ['debug_mode'] = 'yes'
        logging.basicConfig(
            level=logging.getLevelName(level),
            format=Fore.CYAN + '%(asctime)s '
            + Fore.RED + '[%(levelname)s] '
            + Fore.YELLOW + '(%(name)s)\n'
            + Fore.WHITE + '%(message)s' + Fore.RESET,
        )
        debug_mode(level)
    # end if

    if args.suppress:
        input_suppression()
        print(args)
    # end if

    if args.bot:
        os.environ['BOT'] = args.bot
    # end if

    for key, val in args.extra.items():
        os.environ[key] = val[0]
    # end for

    # requests.urllib3.disable_warnings(
    #     requests.urllib3.exceptions.InsecureRequestWarning)
    # # end if
# end def


def start_app():
    init()

    load_sources()
    cancel_method()

    try:
        bot = os.getenv('BOT', '').lower()
        run_bot(bot)
    except Exception as err:
        if os.getenv('debug_mode') == 'yes':
            raise err
        elif not isinstance(err, KeyError):
            error_message(err)
        # end if
    # end try

    epilog()

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        try:
            input('Press ENTER to exit...')
        except EOFError:
            pass
        # end try
    # end if
# end def
