# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace

from ..assets import get_version

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
    dict(flags=('-v', '--version'), action='version',
         version='Lightnovel Crawler ' + get_version()),
    dict(flags=('--config'), dest='config', metavar='CONFIG_FILE',
         help='The config file path'),
    dict(flags=('method'), nargs='?', default='app',
         choices=['app', 'bot', 'configure'],
         help='The method name (default: app)'),
]


def _build(args: list = None, parser: ArgumentParser = None):
    if args is None:
        args: list = globals().get('_arguments')
    if parser is None:
        parser: ArgumentParser = globals().get('_parser')
    for arg in args:
        if isinstance(arg, dict):
            flags = arg.pop('flags', tuple())
            if isinstance(flags, tuple):
                flags = list(flags)
            elif not isinstance(flags, list):
                flags = [flags]
            parser.add_argument(*flags, **arg)
        elif isinstance(arg, list):
            group = parser.add_argument_group()
            _build(arg, group)
        elif isinstance(arg, tuple):
            mutex = parser.add_mutually_exclusive_group()
            _build(arg, mutex)
        else:
            raise ValueError(
                f"Expected list, tuple or dict. Found {type(arg)}")


def get_args() -> Namespace:
    if not globals().get('_parsed'):
        _build()
        globals()['_parsed'] = _parser.parse_args()
    return globals().get('_parsed')
