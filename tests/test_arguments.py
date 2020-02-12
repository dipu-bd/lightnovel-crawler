# -*- coding: utf-8 -*-

import sys
import os
import json
import shutil
import tempfile
import unittest
import logging
from argparse import ArgumentParser, ArgumentError

from src.app.arguments import _build


class TestArguments(unittest.TestCase):
    def test_build_arguments(self):
        parser = ArgumentParser()
        args = [
            dict(args=('-v', '--version'), action='version', version='1.0'),
            dict(args=('--config')),
        ]
        _build(args, parser)
        cfg = parser.parse_args(['--config', 'some file'])
        self.assertEqual(cfg.config, 'some file')

    def test_value_error(self):
        parser = ArgumentParser()
        args = [
            ('bad value'),
            dict(args=('--config')),
        ]
        with self.assertRaises(ValueError):
            _build(args, parser)

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
        _build(args, parser)
        arg = parser.parse_args(['--group', 'one'])
        self.assertEqual(arg.group, 'one')
        self.assertIsNone(arg.arg)
        arg = parser.parse_args(['--arg', 'two'])
        self.assertIsNone(arg.group)
        self.assertEqual(arg.arg, 'two')
        arg = parser.parse_args(['--group', 'one', '--arg', 'two'])
        self.assertEqual(arg.group, 'one')
        self.assertEqual(arg.arg, 'two')

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
        _build(args, parser)
        arg = parser.parse_args(['--mututally', 'one'])
        self.assertEqual(arg.mututally, 'one')
        self.assertIsNone(arg.exclusive)
        arg = parser.parse_args(['--exclusive', 'two'])
        self.assertIsNone(arg.mututally)
        self.assertEqual(arg.exclusive, 'two')
        with self.assertRaises(SystemExit):
            with self.assertRaises(ArgumentError):
                parser.parse_args(['--mututally', 'one', '--exclusive', 'two'])

    def test_duplicate_arguments(self):
        parser = ArgumentParser()
        args = [
            dict(args=('-v', '--version'), action='version', version='1.0'),
            dict(args=('--aaarg')),
            dict(args=('--aaarg')),
        ]
        with self.assertRaises(ArgumentError):
            _build(args, parser)

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
        _build(args, parser)

    def test_args_with_list_and_single_values(self):
        parser = ArgumentParser()
        args = [
            dict(args='--single'),
            dict(args=('--bracket')),
            dict(args=('-m', '--multi')),
        ]
        _build(args, parser)

    def test_args_with_non_str_values(self):
        parser = ArgumentParser()
        args = [
            dict(args=3),
        ]
        with self.assertRaises(TypeError):
            _build(args, parser)
