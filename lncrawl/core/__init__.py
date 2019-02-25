#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""
import os
import logging

import requests
from colorama import init as init_colorama, Fore

from ..bots import run_bot
from ..assets.icons import Icons
from ..assets.version import get_value as get_version
from .arguments import get_args, build_parser
from .display import (description, epilog, debug_mode, url_not_recognized,
                      cancel_method, error_message, new_version_news, input_suppression)

logger = logging.Logger('CORE')


def check_updates():
    try:
        logger.info('Checking version')
        url = 'https://pypi.org/pypi/lightnovel-crawler/json'
        res = requests.get(url, verify=False, timeout=3)
        latest = res.json()['info']['version']
        if get_version() != latest:
            new_version_news(latest)
        # end if
    except Exception as err:
        logger.debug(err)
        error_message('Failed to check for update')
    # end try
# end def


def init():
    os.environ['version'] = get_version()

    init_colorama()
    description()

    build_parser()
    args = get_args()

    levels = ['NOTSET', 'WARN', 'INFO', 'DEBUG']
    level = os.getenv('LOG_LEVEL')
    if not level:
        level = levels[args.log] if args.log else 'NOTSET'
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

    requests.urllib3.disable_warnings(
        requests.urllib3.exceptions.InsecureRequestWarning)
    # end if
# end def


def start_app():
    init()

    check_updates()
    cancel_method()

    try:
        bot = os.getenv('BOT', '').lower()
        run_bot(bot)
    except Exception as err:
        if os.getenv('debug_mode') == 'yes':
            raise err
        else:
            error_message(err)
        # end if
    # end try

    epilog()
# end def
