# -*- coding: utf-8 -*-

import sys
import os
import json
import shutil
import tempfile
import unittest
import logging

from src.app import Config
from src.assets import DEFAULT_CONFIG


class TestConfig(unittest.TestCase):

    def test_config_is_singleton(self):
        '''Test if config is a singleton'''
        instance1 = Config()
        instance2 = Config()
        self.assertEqual(instance1, instance2)

    def test_config_load(self):
        self.assertDictEqual(Config().config, DEFAULT_CONFIG)
        # create a temp config.json
        temp_dir = tempfile.mkdtemp()
        self.assertTrue(os.path.isdir(temp_dir))
        config_file = os.path.join(temp_dir, 'config.json')
        with open(config_file, 'w') as f:
            modified_dict = dict(DEFAULT_CONFIG)
            modified_dict['test'] = 'value'
            f.write(json.dumps(modified_dict, indent=2))
        self.assertTrue(os.path.isdir(temp_dir))
        # load config
        Config()._config_file_ = config_file
        self.assertEqual(Config().config_file, config_file)
        Config().load()
        self.assertEqual(Config().config['test'], 'value')
        # remove temp dir and reset
        shutil.rmtree(temp_dir)
        self.assertFalse(os.path.exists(temp_dir))
        Config().__init__()
        self.assertIsNone(Config().config.get('test'))

    def test_config_save(self):
        self.assertDictEqual(Config().config, DEFAULT_CONFIG)
        # create a temp config.json
        temp_dir = tempfile.mkdtemp()
        self.assertTrue(os.path.isdir(temp_dir))
        config_file = os.path.join(temp_dir, 'config.json')
        # save config to temp file
        Config()._config_file_ = config_file
        self.assertEqual(Config().config_file, config_file)
        Config().save()
        self.assertTrue(os.path.isfile(config_file))
        # test written value
        saved_config = None
        with open(config_file, 'r') as f:
            saved_config = json.loads(f.read())
        self.assertDictEqual(saved_config, DEFAULT_CONFIG)
        # remove temp dir
        shutil.rmtree(temp_dir)
        self.assertFalse(os.path.exists(temp_dir))

    def test_defaults_is_singleton(self):
        default1 = Config().defaults
        default2 = Config().defaults
        self.assertEqual(default1, default2)

    def test_logging_is_singleton(self):
        logging1 = Config().logging
        logging2 = Config().logging
        self.assertEqual(logging1, logging2)

    def test_defaults_properties(self):
        self.assertEqual(str(Config().defaults.work_directory),
                         DEFAULT_CONFIG['defaults']['work_directory'])

    def test_logging_properties(self):
        self.assertEqual(Config().logging.root_log_level,
                         DEFAULT_CONFIG['logging']['loggers']['']['level'])
        self.assertListEqual(Config().logging.root_log_handlers,
                             DEFAULT_CONFIG['logging']['loggers']['']['handlers'])

    def test_work_directory_setter(self):
        directory = Config().defaults.work_directory
        modified_name = 'Lightnovel Crawler [test_work_directory_setter]'
        modified = directory / '..' / modified_name
        Config().defaults.work_directory = modified
        expected_value = directory.parent / modified_name
        self.addCleanup(shutil.rmtree, expected_value)
        self.assertEqual(expected_value, Config().defaults.work_directory)
        self.assertTrue(os.path.exists(expected_value))
        Config().defaults.work_directory = directory
        self.assertEqual(directory, Config().defaults.work_directory)
