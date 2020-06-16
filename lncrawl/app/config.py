# -*- coding: utf-8 -*-

import atexit
import logging
import os
from typing import Any, Mapping

import yaml

from .utility.colors import Color
from .utility.dictionary import DictUtils, PathType


class _Config:
    __opened_file__ = None

    __config_files__ = [
        os.path.abspath('config.yaml'),
        os.path.join(os.path.expanduser('~'), 'dwse', 'config.yaml'),
    ]

    # Define configurations here
    __dict__: Mapping[str, Any] = {
        'browser': {
            'parser': 'html5lib',
            'stream_chunk_size':  50 * 1024,  # in bytes
            'cloudscraper': {
                # Docs: https://github.com/VeNoMouS/cloudscraper
                'debug': False,
                'allow_brotli': False,
                'browser': {
                    'mobile': False
                },
                'delay': None,
                'interpreter': 'native',
                'recaptcha': None,
            },
        },
        'concurrency': {
            'max_connections': 1000,
            'max_workers': 10,
            'per_host': {
                'max_connections': 10,
                'semaphore_timeout': 5 * 60,  # seconds
            }
        },
        'sources': {
            # override source specific config here
            'en.lnmtl': {
                'concurrency': {
                    'max_workers': 2
                }
            }
        },
        'logging': {
            #
            # Configure logging
            # Docs: https://docs.python.org/3.5/library/logging.config.html#configuration-dictionary-schema
            # Example: https://stackoverflow.com/a/7507842/1583052
            #
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'console': {
                    'format': f'{Color.CYAN}%(asctime)s{Color.RESET} {Color.BLUE}%(levelname)-8s{Color.RESET} %(message)s',
                    'datefmt': '%H:%M:%S',
                },
                'file': {
                    'format': '%(asctime)s [%(process)d] %(levelname)s\n@%(name)s: %(message)s\n',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
            },
            'handlers': {
                'console': {
                    'formatter': 'console',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',  # default is stderr
                },
                'file': {
                    'formatter': 'file',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'lncrawl.log',
                    'maxBytes': 1024 * 1024,  # 1 MB
                    'backupCount': 3,
                },
            },
            'loggers': {
                '': {  # root logger
                    'handlers': ['console'],
                    'level': logging.getLevelName(logging.INFO),
                },
            },
        },
    }

    def __init__(self):
        self._load()

    def _load(self) -> None:
        try:
            for filepath in self.__config_files__:
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    self.__opened_file__ = filepath
                    with open(self.__opened_file__, 'r', encoding='utf-8') as fp:
                        data = yaml.safe_load(fp)
                        DictUtils.merge(self.__dict__, data)
                        logging.info(f'Load config from {self.__opened_file__}')
                        return  # exit after first load
        except Exception:
            logging.exception('Failed to load config')
        finally:
            atexit.register(self._save)  # save at exit

    def _save(self) -> None:
        if not self.__opened_file__:
            self.__opened_file__ = self.__config_files__[1]
        try:
            os.makedirs(os.path.dirname(self.__opened_file__), exist_ok=True)
            with open(self.__opened_file__, 'w', encoding='utf-8') as fp:
                yaml.safe_dump(self.__dict__, fp)
                logging.info(f'Saved config to {self.__opened_file__}')
        except Exception:
            logging.exception('Failed to save config')

    def get(self, path: PathType, default: Any = None) -> Any:
        return DictUtils.get_value(self.__dict__, path, default)

    def put(self, path: PathType, value: Any) -> None:
        DictUtils.put_value(self.__dict__, path, value)

    def scraper(self, scraper_name: str, path: PathType, fallback: Any = None) -> Any:
        '''Returns config specific to a source'''
        default = self.get(path)
        scraper = self.get(['sources', scraper_name, path])
        if scraper is None:
            return default
        if isinstance(scraper, dict) and isinstance(default, dict):
            return DictUtils.merge({}, default, scraper)
        return scraper


CONFIG = _Config()
