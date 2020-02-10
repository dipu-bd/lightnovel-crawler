# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser, Namespace
from typing import List, Mapping, Any
from ...assets.variables import *


class ArgumentBuilder:
    def __init__(self, *args: str, mutex: List['Argument'] = [], group: List['Argument'] = [], **kargs: Any):
        '''Initialize an argument. Check argparse.ArgumentParser.add_argument() for available parameters'''
        self.args = args
        self.kargs = kargs
        self.group = group
        self.mutex = mutex

    def build(self, parser: ArgumentParser = None):
        '''Create ArgumentParser from '''
        if not parser:
            usage: str = '[options...] input'
            parser = ArgumentParser(
                prog=APP_FULL_NAME,
                epilog='~' * CONSOLE_MAX_LINES,
                usage=f"{APP_SHORT_NAME} {usage}\n{APP_FULL_NAME} {usage}"
            )

        if len(self.args) or len(self.kargs):
            parser.add_argument(*self.args, **self.kargs)

        if len(self.group):
            arg_group = parser.add_argument_group()
            for arg in self.group:
                arg.build(arg_group)

        if len(self.mutex):
            mutex_group = parser.add_mutually_exclusive_group()
            for arg in self.mutex:
                arg.build(mutex_group)

        return parser

    def parse(self) -> Namespace:
        if not hasattr(self, 'arguments'):
            args = self.build().parse_args()
            setattr(self, 'arguments', args)
        return self.arguments
