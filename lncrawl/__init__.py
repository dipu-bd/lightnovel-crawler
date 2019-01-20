#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dotenv import load_dotenv

from .core import start_app
from .utils.crawler import Crawler
from .bots.telegram import telegram_bot

load_dotenv()

def main():
    start_app()
# end def

if __name__ == '__main__':
    main()
# end if
