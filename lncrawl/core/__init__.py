#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""
import os
import logging

import requests
from dotenv import load_dotenv
from colorama import init as init_colorama, Fore

from ..assets.icons import Icons
from ..assets.version import get_value as get_version
from .arguments import get_args, build_parser
from .display import (description, epilog, debug_mode, url_not_recognized,
                      cancel_method, error_message, new_version_news, input_suppression)

from .app import App
from ..bots import telegram

logger = logging.Logger('APP_ROOT')


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
    load_dotenv()
    os.environ['version'] = get_version()

    init_colorama()
    description()

    build_parser()
    args = get_args()

    if args.log:
        os.environ['debug_mode'] = 'true'
        levels = [None, logging.WARN, logging.INFO, logging.DEBUG]
        logging.basicConfig(
            level=levels[args.log],
            format=Fore.CYAN + '%(asctime)s '
            + Fore.RED + '[%(levelname)s] '
            + Fore.YELLOW + '(%(name)s)\n'
            + Fore.WHITE + '%(message)s' + Fore.RESET,
        )
        debug_mode(args.log)
    # end if

    if args.suppress:
        input_suppression()
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
        if bot == 'telegram':
            telegram.main()
        else:
            App().start()
        # end def
    except Exception as err:
        if os.getenv('debug_mode') == 'true':
            raise err
        else:
            error_message(err)
        # end if
    # end try

    epilog()

    if Icons.isWindows:
        input('Press ENTER to exit...')
    # end if
# end def
