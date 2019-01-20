#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    bot = os.getenv('BOT', '').lower()
    if bot == 'telegram':
        from .bots.telegram import start_app
        start_app()
    else:
        from .core import start_app
        start_app()
    # end def
# end def


if __name__ == '__main__':
    main()
# end if
