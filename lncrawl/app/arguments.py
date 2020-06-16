# -*- coding: utf-8 -*-
import os
import sys
from argparse import ArgumentParser, Namespace

from ..version import VERSION
from .utility.arg_builder import arg_builder

_parsed_args = None

_parser = ArgumentParser(
    epilog='~' * 78,
    # usage="lnc [options...]\n"
    # "       lncrawl [options...]\n"
    # "       lightnovel-crawler [options...]"
)


# Use a dictionary to add new argument
# Use tuple for mutually exclusive group
# Use list for a simple group
_arguments = [
    dict(args=('-v', '--version'), action='version',
         version='Lightnovel Crawler ' + VERSION),
    dict(args=('-c, --config'), dest='config', metavar='CONFIG_FILE',
         help='The config file path'),
]


def get_args() -> Namespace:
    args = sys.argv[1:]
    if os.getenv('MODE') == 'TEST':
        args = []

    global _parsed_args
    if _parsed_args is None:
        global _parser, _arguments
        build_args(_parser, _arguments)
        _parsed_args = _parser.parse_args(args)
    return _parsed_args
