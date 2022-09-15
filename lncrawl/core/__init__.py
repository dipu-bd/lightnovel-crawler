# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""
import logging
import os
import sys
import signal
import colorama
import urllib3
from colorama import Fore

from ..assets.version import get_version
from ..bots import run_bot
from .arguments import get_args
from .display import (cancel_method, debug_mode, description, error_message,
                      input_suppression)
from .proxy import start_proxy_fetcher, stop_proxy_fetcher, load_proxies
from .sources import load_sources

logger = logging.getLogger(__name__)

def destroy(*args, **kwargs):
    error_message('', 'Cancelled by user', None)
    stop_proxy_fetcher()
    sys.exit(1)
# end def
    

def init():
    os.environ['version'] = get_version()
    signal.signal(signal.SIGINT, destroy)

    colorama.init(wrap=True)
    description()

    args = get_args()

    levels = ['NOTSET', 'WARN', 'INFO', 'DEBUG']
    level = os.getenv('LOG_LEVEL')
    if not level:
        level = levels[args.log] if args.log else 'NOTSET'
        os.environ['LOG_LEVEL'] = level
        urllib3.disable_warnings()
    # end if
    if level != 'NOTSET':
        os.environ['debug_mode'] = 'yes'
        urllib3.add_stderr_logger(logging.INFO)
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

    args = get_args()
    if args.proxy_file:
        os.environ['use_proxy'] = '1'
        load_proxies(args.proxy_file)
    # end if
    if args.auto_proxy:
        os.environ['use_proxy'] = '1'
        start_proxy_fetcher()
    # end if

    try:
        bot = os.getenv('BOT', '').lower()
        run_bot(bot)
    except Exception as e:
        if not isinstance(e, KeyboardInterrupt):
            error_message(*sys.exc_info())
        # end if
    # end try

    if args.auto_proxy:
        stop_proxy_fetcher()
    # end if

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS') and not args.close_directly:
        try:
            input('Press ENTER to exit...')
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass
        # end try
    # end if
# end def
