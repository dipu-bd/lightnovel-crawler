# -*- coding: utf-8 -*-
import os

from src.app.config import CONFIG
from src.assets import DEFAULT_CONFIG


class TestConfig:

    def test_config_save_and_load(self):
        assert CONFIG is not None
        assert CONFIG.config_file is not None
        CONFIG.save()
        assert os.path.isfile(CONFIG.config_file)
        CONFIG.load()

    def test_config_is_singleton(self):
        '''Test if config is a singleton'''
        instance1 = CONFIG
        instance2 = CONFIG
        assert instance1 == instance2

    def test_config_is_independent(self):
        CONFIG.config['prop'] = 'ok'
        assert 'prop' not in DEFAULT_CONFIG
        del CONFIG.config['prop']

    def test_arguments_is_singleton(self):
        instance1 = CONFIG.arguments
        instance2 = CONFIG.arguments
        assert instance1 == instance2

    def test_logging_is_singleton(self):
        instance1 = CONFIG.logging
        instance2 = CONFIG.logging
        assert instance1 == instance2
        instance1.__data__['prop'] = 'logging'
        assert 'prop' in CONFIG.logging.__data__
        assert 'prop' in CONFIG.config['logging']
        del instance1.__data__['prop']

    def test_browser_is_singleton(self):
        instance1 = CONFIG.browser
        instance2 = CONFIG.browser
        assert instance1 == instance2
        instance1.__data__['prop'] = 'browser'
        assert 'prop' in CONFIG.browser.__data__
        assert 'prop' in CONFIG.config['browser']
        del instance1.__data__['prop']

    def test_logging_properties(self):
        assert CONFIG.logging.root_log_level == \
            DEFAULT_CONFIG['logging']['loggers']['']['level']
        assert CONFIG.logging.root_log_handlers == \
            DEFAULT_CONFIG['logging']['loggers']['']['handlers']

    def test_browser_config(self):
        assert CONFIG.browser is not None
        assert isinstance(CONFIG.browser.concurrent_requests, int)
        assert CONFIG.browser.soup_parser == 'html5lib'
        assert CONFIG.browser.cloudscraper is not None
        assert CONFIG.browser.response_timeout is None
        assert isinstance(CONFIG.browser.stream_chunk_size, int)
