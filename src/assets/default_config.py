# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from .colors import Color

# Docs: https://docs.python.org/3/library/configparser.html
DEFAULT_CONFIG = {
    # Browser configuration
    'browser': {
        'concurrent_requests': 5,
        'soup_parser': 'html5lib',
        'response_timeout': None,
        'stream_chunk_size': 50 * 1024,
        'cloudscraper': {
            #
            # Configure cloudscraper instance
            # Docs: https://github.com/VeNoMouS/cloudscraper
            #
            'debug': False,
            'allow_brotli': False,
            'browser': {
                'browser': 'firefox',
                'mobile': False
            },
            'delay': None,
            'interpreter': 'native',
            'recaptcha': None,
        },
    },

    # Logger configuration
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
