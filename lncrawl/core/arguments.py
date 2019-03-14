#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import textwrap
from urllib.parse import parse_qs

from .display import LINE_SIZE
from ..bots import supported_bots
from ..binders import available_formats


class ArgReader:
    def build(self):
        parser = argparse.ArgumentParser(
            prog='lncrawl',
            epilog='~'*LINE_SIZE,
            usage='lncrawl [options...]\n'
            '       lightnovel-crawler [options...]'
        )
        parser.add_argument('-l', dest='log', action='count',
                            help='Set log levels (1 = warn, 2 = info, 3 = debug)')
        parser.add_argument('-v', '--version', action='version',
                            version='Lightnovel Crawler ' + os.getenv('version'))

        source = parser.add_mutually_exclusive_group()
        # source.add_argument('--test', action='store_true',
        #                     help='Start in test environment')
        source.add_argument('-s', '--source', dest='novel_page', type=str, metavar='URL',
                            help='Profile page url of the novel')
        source.add_argument('-q', '--query', dest='query', type=str, metavar='STR',
                            help='Novel query followed by list of source sites.')

        parser.add_argument('--sources',  action='store_true',
                            help='Display the source selection menu while searching')

        parser.add_argument('-o', '--output', dest='output_path', type=str, metavar='PATH',
                            help='Path where the downloads to be stored')
        parser.add_argument('--format', dest='output_formats', nargs='+', metavar='E',
                            choices=available_formats, default=[],
                            help='Define which formats to output. Default: all')

        replacer = parser.add_mutually_exclusive_group()
        replacer.add_argument('-f', '--force', action='store_true',
                              help='Force replace any existing folder')
        replacer.add_argument('-i', '--ignore', action='store_true',
                              help='Ignore any existing folder (do not replace)')

        byvol = parser.add_mutually_exclusive_group()
        byvol.add_argument('--single', action='store_true',
                           help='Put everything in a single book')
        byvol.add_argument('--multi', action='store_true',
                           help='Build separate books by volumes')

        parser.add_argument('--login', nargs=2, metavar=('USER', 'PASSWD'),
                            help='User name/email address and password for login')

        selection = parser.add_mutually_exclusive_group()
        selection.add_argument('--all', action='store_true',
                               help='Download all chapters')
        selection.add_argument('--first', type=int, nargs='?', metavar='COUNT',
                               help='Download first few chapters (default: 10)')
        selection.add_argument('--last', type=int, nargs='?', metavar='COUNT',
                               help='Download last few chapters (default: 10)')
        selection.add_argument('--page', type=str, nargs=2, metavar=('START', 'STOP'),
                               help='The start and final chapter urls')
        selection.add_argument('--range', type=int, nargs=2, metavar=('FROM', 'TO'),
                               help='The start and final chapter indexes')
        selection.add_argument('--volumes', type=int, nargs='*', metavar='N',
                               help='The list of volume numbers to download')
        selection.add_argument('--chapters', nargs='*', metavar='URL',
                               help='A list of specific chapter urls')

        parser.add_argument('--suppress', action='store_true',
                            help='Suppress input prompts (use defaults instead)')

        parser.add_argument('--bot', type=str, choices=supported_bots,
                            help='Select a bot. Default: console')

        parser.add_argument('extra', type=parse_qs, nargs='?', metavar='EXTRA', default={},
                            help='To pass a query string to use as extra arguments')

        self.arguments = parser.parse_args()
# end class


reader = ArgReader()


def build_parser():
    reader.build()
# end def


def get_args():
    return reader.arguments
# end def
