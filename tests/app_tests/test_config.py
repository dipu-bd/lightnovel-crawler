# -*- coding: utf-8 -*-

import sys
import os
import json
import shutil
import tempfile
import unittest
import logging
import atexit

from src.app import CONFIG
from src.assets import DEFAULT_CONFIG


class TestConfig(unittest.TestCase):

    def test_config_save_and_load(self):
        self.assertIsNotNone(CONFIG.config_file)
        CONFIG.save()
        self.assertTrue(os.path.isfile(CONFIG.config_file))
        CONFIG.load()

    def test_config_is_singleton(self):
        '''Test if config is a singleton'''
        instance1 = CONFIG
        instance2 = CONFIG
        self.assertEqual(instance1, instance2)

    def test_config_is_independent(self):
        CONFIG.config['prop'] = 'ok'
        self.assertTrue('prop' not in DEFAULT_CONFIG)
        del CONFIG.config['prop']

    def test_arguments_is_singleton(self):
        instance1 = CONFIG.arguments
        instance2 = CONFIG.arguments
        self.assertEqual(instance1, instance2)

    def test_logging_is_singleton(self):
        instance1 = CONFIG.logging
        instance2 = CONFIG.logging
        self.assertEqual(instance1, instance2)
        instance1.__data__['prop'] = 'logging'
        self.assertTrue('prop' in CONFIG.logging.__data__)
        self.assertTrue('prop' in CONFIG.config['logging'])
        del instance1.__data__['prop']

    def test_browser_is_singleton(self):
        instance1 = CONFIG.browser
        instance2 = CONFIG.browser
        self.assertEqual(instance1, instance2)
        instance1.__data__['prop'] = 'browser'
        self.assertTrue('prop' in CONFIG.browser.__data__)
        self.assertTrue('prop' in CONFIG.config['browser'])
        del instance1.__data__['prop']

    def test_logging_properties(self):
        self.assertEqual(CONFIG.logging.root_log_level,
                         DEFAULT_CONFIG['logging']['loggers']['']['level'])
        self.assertListEqual(CONFIG.logging.root_log_handlers,
                             DEFAULT_CONFIG['logging']['loggers']['']['handlers'])

    def test_browser_config(self):
        self.assertIsNotNone(CONFIG.browser)
        self.assertEqual(CONFIG.browser.concurrent_requests, 5)
        self.assertEqual(CONFIG.browser.soup_parser, 'html5lib')
