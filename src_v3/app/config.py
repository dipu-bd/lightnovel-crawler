# -*- coding: utf-8 -*-

import json
import logging
import logging.config
import os
from pathlib import Path, PurePath
from typing import *

from ..assets import DEFAULT_CONFIG
from ..meta import Singleton
from .arguments import get_args


class Config(metaclass=Singleton):
    '''Access and manage app configurations'''

    def __init__(self) -> None:
        # Load default configuration
        self.config = dict(DEFAULT_CONFIG)

        # Load configuration from file
        self.load()

        # Initialize logger
        logging.config.dictConfig(self.logging.section)

    def load(self) -> None:
        '''Loads config from a file'''
        if not os.path.isfile(self.config_file):
            return
        with open(self.config_file, mode='r', encoding='utf-8') as fp:
            config: dict = json.load(fp)
            self.config.update(config)

    def save(self) -> None:
        '''Saves config to a file'''
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, mode='w', encoding='utf-8') as fp:
            json.dump(self.config, fp, indent=2)

    # ========================================================================= #
    # Property declarations for easy access                                     #
    # ========================================================================= #

    class __Section__(metaclass=Singleton):
        def __init__(self, data: Mapping[str, Any]):
            setattr(self, 'section', data)

    class _Arguments(metaclass=Singleton):
        def __init__(self):
            setattr(self, 'section', get_args().__dict__)

        @property
        def config(self):
            return self.section.get('config')

    class _Defaults(__Section__):
        @property
        def work_directory(self) -> PurePath:
            fallback = str(Path(os.getcwd()) / 'Lightnovels')
            return Path(self.section.get('work_directory', fallback))

    class _Logging(__Section__):
        @property
        def loggers(self) -> dict:
            return self.section.get('loggers', {})

        @property
        def handlers(self) -> dict:
            return self.section.get('handlers', {})

        @property
        def root_log_level(self) -> str:
            return self.loggers.get('', {}).get('level', 'NOTSET')

        @property
        def root_log_handlers(self) -> List[str]:
            return self.loggers.get('', {}).get('handlers', [])

    @property
    def arguments(self) -> _Arguments:
        return self._Arguments()

    @property
    def defaults(self) -> _Defaults:
        return self._Defaults(self.config['defaults'])

    @property
    def logging(self) -> _Logging:
        return self._Logging(self.config['logging'])

    @property
    def config_file(self) -> str:
        if not hasattr(self, '_config_file_'):
            fname = str(self.defaults.work_directory / 'config.json')
            setattr(self, '_config_file_', self.arguments.config or fname)
        return getattr(self, '_config_file_', '')
