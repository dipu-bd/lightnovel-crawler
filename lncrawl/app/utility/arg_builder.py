# -*- coding: utf-8 -*-

from argparse import _ActionsContainer


def build_args(parser: _ActionsContainer, arguments: list):
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
            build_args(group, kwarg)
        elif isinstance(kwarg, tuple):
            mutex = parser.add_mutually_exclusive_group()
            build_args(mutex, list(kwarg))
        else:
            raise ValueError(f"{type(kwarg)}[{kwarg}]")
