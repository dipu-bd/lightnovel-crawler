#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
from .console import ConsoleInterface
from .telegram import TelegramInterface

logger = logging.getLogger('BOT')


def get_bot():
    bot = os.getenv('BOT', '').lower()
    logger.info('Using `%s` Bot' % bot)

    if bot == 'telegram.py':
        return TelegramInterface()
    else:
        return ConsoleInterface()
    # end def
# end def
