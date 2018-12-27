#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive value input"""
from .core import start_app
from .utils.crawler import Crawler
from .tests.crawler_app_test import run_tests
from .spiders import crawler_list

def main():
    start_app(crawler_list)
# end def


if __name__ == '__main__':
    main()
# end if
