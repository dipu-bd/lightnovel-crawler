# -*- coding: utf-8 -*-
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
    dict(args=('--config'), dest='config', metavar='CONFIG_FILE',
         help='The config file path'),
    dict(args=('method'), nargs='?', default='app',
         choices=['app', 'bot', 'configure'],
         help='The method name (default: app)'),
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
    global _parsed_args
    if _parsed_args is None:
        _build()
        _parsed_args = _parser.parse_args()
    return _parsed_args
