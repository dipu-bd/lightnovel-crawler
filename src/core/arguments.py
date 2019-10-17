#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
from urllib.parse import parse_qs

from .display import LINE_SIZE
from ..bots import supported_bots
from ..binders import available_formats
from ..assets.version import get_value as get_version


class Args:
    def __init__(self, * args, mutex: list = [], group: list = [], **kargs):
        self.args = args
        self.kargs = kargs
        self.group = group
        self.mutex = mutex
        self.arguments = None
    # end def

    def build(self, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser(
                prog='lncrawl',
                epilog='~'*LINE_SIZE,
                usage='lncrawl [options...]\n'
                '       lightnovel-crawler [options...]'
            )
        # end if
        if len(self.args) or len(self.kargs):
            parser.add_argument(*self.args, **self.kargs)
        # end if
        if len(self.group):
            arg_group = parser.add_argument_group()
            for arg in self.group:
                arg.build(arg_group)
            # end for
        # end if
        if len(self.mutex):
            mutex_group = parser.add_mutually_exclusive_group()
            for arg in self.mutex:
                arg.build(mutex_group)
            # end for
        # end if
        return parser
    # end def

    def get_args(self):
        if self.arguments is None:
            self.arguments = self.build().parse_args()
        # end if
        return self.arguments
    # end def
# end class


_builder = Args(group=[
    Args('-v', '--version', action='version',
         version='Lightnovel Crawler ' + get_version()),
    Args('-l', dest='log', action='count',
         help='Set log levels. (-l = warn, -ll = info, -lll = debug).'),

    Args('--list-sources',  action='store_true',
         help='Display a list of available sources.'),

    Args(mutex=[
        Args('-s', '--source', dest='novel_page', type=str, metavar='URL',
             help='Profile page url of the novel.'),
        Args(group=[
            Args('-q', '--query', dest='query', type=str, metavar='STR',
                 help='Novel query followed by list of source sites.'),
            Args('-x', '--sources', dest='sources', action='store_true',
                 help='Display the source selection menu while searching.'),
        ]),
    ]),

    Args(group=[
        Args('-o', '--output', dest='output_path', type=str, metavar='PATH',
             help='Path where the downloads to be stored.'),
        Args('--format', dest='output_formats', nargs='+', metavar='E',
             choices=available_formats, default=list(),
             help='Define which formats to output. Default: all.'),
        Args('--add-source-url', action='store_true',
             help='Add source url at the end of each chapter.'),
        Args(mutex=[
            Args('--single', action='store_true',
                 help='Put everything in a single book.'),
            Args('--multi', action='store_true',
                 help='Build separate books by volumes.'),
        ]),
    ]),
    Args(mutex=[
        Args('-f', '--force', action='store_true',
             help='Force replace any existing folder.'),
        Args('-i', '--ignore', action='store_true',
             help='Ignore any existing folder (do not replace).'),
    ]),

    Args('--login', nargs=2, metavar=('USER', 'PASSWD.'),
         help='User name/email address and password for login.'),

    Args(mutex=[
        Args('--all', action='store_true',
             help='Download all chapters.'),
        Args('--first', type=int, nargs='?', metavar='COUNT',
             help='Download first few chapters (default: 10).'),
        Args('--last', type=int, nargs='?', metavar='COUNT',
             help='Download last few chapters (default: 10).'),
        Args('--page', type=str, nargs=2, metavar=('START', 'STOP.'),
             help='The start and final chapter urls.'),
        Args('--range', type=int, nargs=2, metavar=('FROM', 'TO.'),
             help='The start and final chapter indexes.'),
        Args('--volumes', type=int, nargs='*', metavar='N',
             help='The list of volume numbers to download.'),
        Args('--chapters', nargs='*', metavar='URL',
             help='A list of specific chapter urls.'),
    ]),

    Args('--bot', type=str, choices=supported_bots,
         help='Select a bot. Default: console.'),

    Args('--suppress', action='store_true',
         help='Suppress all input prompts and use defaults.'),

    Args('extra', type=parse_qs, nargs='?', metavar='ENV', default=dict(),
         help='[chatbots only] Pass query string at the end of all options. '
         'It will be use instead of .env file. '
         'Sample: "BOT=discord&DISCORD_TOKEN=***&LOG_LEVEL=DEBUG"'),
])


def get_args():
    return _builder.get_args()
# end def
