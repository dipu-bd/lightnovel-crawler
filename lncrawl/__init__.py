#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dotenv import load_dotenv

from .core import start_app
from .utils.crawler import Crawler

load_dotenv()

def main():
    start_app()
# end def

if __name__ == '__main__':
    main()
# end if
