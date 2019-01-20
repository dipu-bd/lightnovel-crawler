#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from .console import ConsoleInterface
from .telegram import TelegramInterface


def get_bot():
    bot = os.getenv('BOT', '').lower()
    if bot == 'telegram.py':
        return TelegramInterface()
    else:
        return ConsoleInterface()
    # end def
# end def
