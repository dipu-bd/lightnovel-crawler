# -*- coding: utf-8 -*-
import os
import logging
import logging.config
from colorama import Fore
from ...core.arguments import get_args

# The special signal character for crawler commands
signal = os.getenv('DISCORD_SIGNAL_CHAR') or '!'
max_workers = int(os.getenv('DISCORD_MAX_WORKERS', 10))

# The public ip and path of the server to put files in
public_ip = os.getenv('PUBLIC_ADDRESS', None)
public_path = os.getenv('PUBLIC_DATA_PATH', None)

os.makedirs('logs', exist_ok=True)
logging.config.dictConfig({
    #
    # Configure logging
    # Docs: https://docs.python.org/3.5/library/logging.config.html#configuration-dictionary-schema
    # Example: https://stackoverflow.com/a/7507842/1583052
    #
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'console': {
            'format': Fore.CYAN+'%(asctime)s'+Fore.RESET + ' ' + Fore.GREEN + '%(levelname)-8s'+Fore.RESET+' %(message)s',
            'datefmt': '%H:%M:%S',
        },
        'file': {
            'format': '%(asctime)s [%(process)d] %(levelname)s\n%(name)s: %(message)s\n',
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
            'filename': 'logs/discord-bot_%s.log' % (get_args().shard_id),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'encoding': 'utf8',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': logging.INFO,
        },
    },
})
