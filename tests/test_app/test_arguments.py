# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentError, ArgumentParser

import pytest

from lncrawl.app.utility.arg_builder import build_args


class TestArguments:

    def test_build_arguments(self):
        parser = ArgumentParser()
        args = [
            dict(args=('-v', '--version'), action='version', version='1.0'),
            dict(args=('--config')),
        ]
        build_args(parser, args)
        cfg = parser.parse_args(['--config', 'some file'])
        assert cfg.config == 'some file'

    def test_value_error(self):
        parser = ArgumentParser()
        args = [
            ('bad value'),
            dict(args=('--config')),
        ]
        with pytest.raises(ValueError):
            build_args(parser, args)

    def test_argument_group(self):
        parser = ArgumentParser()
        args = [
            dict(args=('-v', '--version'), action='version', version='1.0'),
            [
                dict(args=('--group')),
                dict(args=('--arg')),
                dict(args=('--more')),
            ]
        ]
        build_args(parser, args)
        arg = parser.parse_args(['--group', 'one'])
        assert arg.group == 'one'
        assert arg.arg is None
        arg = parser.parse_args(['--arg', 'two'])
        assert arg.group is None
        assert arg.arg == 'two'
        arg = parser.parse_args(['--group', 'one', '--arg', 'two'])
        assert arg.group == 'one'
        assert arg.arg == 'two'

    def test_mutually_exclusive_argument(self):
        parser = ArgumentParser()
        args = [
            dict(args=('-v', '--version'), action='version', version='1.0'),
            (
                dict(args=('--mututally')),
                dict(args=('--exclusive')),
                dict(args=('--more')),
            )
        ]
        build_args(parser, args)
        arg = parser.parse_args(['--mututally', 'one'])
        assert arg.mututally == 'one'
        assert arg.exclusive is None
        arg = parser.parse_args(['--exclusive', 'two'])
        assert arg.mututally is None
        assert arg.exclusive == 'two'
        with pytest.raises(SystemExit):
            with pytest.raises(ArgumentError):
                # disable error log from parser
                setattr(parser, 'error', lambda x: sys.exit())
                # parse invalid mutex group
                parser.parse_args(['--mututally', 'one', '--exclusive', 'two'])

    def test_duplicate_arguments(self):
        parser = ArgumentParser()
        args = [
            dict(args=('-v', '--version'), action='version', version='1.0'),
            dict(args=('--aaarg')),
            dict(args=('--aaarg')),
        ]
        with pytest.raises(ArgumentError):
            build_args(parser, args)

    def test_multi_level_of_hierarchy(self):
        parser = ArgumentParser()
        args = [
            dict(args=('-v', '--version'), action='version', version='1.0'),
            (
                dict(args=('--mututally')),
                dict(args=('--exclusive')),
            ),
            dict(args=('--padded')),
            [
                dict(args=('--group')),
                dict(args=('--arg')),
                (
                    dict(args=('--mututal_in_group')),
                    dict(args=('--exclusive_in_group')),
                    [
                        dict(args=('--inner_group')),
                        dict(args=('--inner_arg')),
                    ]
                ),
            ],
            dict(args=('--more')),
            [
                dict(args='--another'),
                dict(args='--group_2'),
            ]
        ]
        build_args(parser, args)

    def test_args_with_list_and_single_values(self):
        parser = ArgumentParser()
        args = [
            dict(args='--single'),
            dict(args=('--bracket')),
            dict(args=('-m', '--multi')),
        ]
        build_args(parser, args)

    def test_args_with_non_str_values(self):
        parser = ArgumentParser()
        args = [
            dict(args=3),
        ]
        with pytest.raises(TypeError):
            build_args(parser, args)
