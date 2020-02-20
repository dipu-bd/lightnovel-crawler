# -*- coding: utf-8 -*-
import sys
import os
from argparse import ArgumentParser, Namespace

from ..assets import get_version

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
         version='Lightnovel Crawler ' + get_version()),
    dict(args=('-c, --config'), dest='config', metavar='CONFIG_FILE',
         help='The config file path'),
]


def _build(arguments: list = None, parser: ArgumentParser = None):
    if arguments is None:
        arguments: list = globals().get('_arguments')
    if parser is None:
        parser: ArgumentParser = globals().get('_parser')
    for kwarg in arguments:
        if isinstance(kwarg, dict):
            args = kwarg.pop('args', tuple())
            if isinstance(args, tuple):
                args = list(args)
            elif not isinstance(args, list):
                args = [args]
            parser.add_argument(*args, **kwarg)
        elif isinstance(kwarg, list):
            group = parser.add_argument_group()
            _build(kwarg, group)
        elif isinstance(kwarg, tuple):
            mutex = parser.add_mutually_exclusive_group()
            _build(kwarg, mutex)
        else:
            raise ValueError(f"{type(kwarg)}[{kwarg}]")


def get_args() -> Namespace:
    args = sys.argv[1:]
    if os.getenv('MODE') == 'TEST':
        args = []

    global _parsed_args
    if _parsed_args is None:
        _build()
        _parsed_args = _parser.parse_args(args)

    return _parsed_args
