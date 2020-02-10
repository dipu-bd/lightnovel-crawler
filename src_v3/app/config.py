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

    def __init__(self):
        # Load default configuration
        self._config: Mapping[str, Any] = dict(DEFAULT_CONFIG)

        # Resolve config file path
        args = get_args()
        self._config_file = args.config or str(
            self.defaults.work_directory / 'config.json')

        # Load configuration from file
        self.load()

        # Initialize logger
        logging.config.dictConfig(self.logging.__data__)
        logging.info("Log initialized")

    def load(self) -> None:
        '''Loads config from a file'''
        if not os.path.isfile(self._config_file):
            return
        with open(self._config_file, mode='r', encoding='utf-8') as fp:
            config = json.load(fp)
            self._config.update(config)

    def save(self) -> None:
        '''Saves config to a file'''
        os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
        with open(self._config_file, mode='w', encoding='utf-8') as fp:
            json.dump(self._config, fp, indent=2)

    # ========================================================================= #
    # Property declarations for easy access                                     #
    # ========================================================================= #

    class __Section__(metaclass=Singleton):
        def __init__(self, data: Mapping[str, Any]):
            setattr(self, '__data__', data)

    class _Defaults(__Section__):
        @property
        def work_directory(self) -> PurePath:
            fallback = str(Path(os.getcwd()) / 'Lightnovels')
            return Path(self.__data__.get('work_directory', fallback))

    class _Logging(__Section__):
        @property
        def root_log_level(self) -> str:
            loggers = self.__data__.get('loggers', {})
            return loggers.get('', {}).get('level', 'NOTSET')

        @property
        def root_log_handlers(self) -> List[str]:
            loggers = self.__data__.get('loggers', {})
            return loggers.get('', {}).get('handlers', [])

    @property
    def defaults(self) -> Optional[_Defaults]:
        return self._Defaults(self._config['defaults'])

    @property
    def logging(self) -> Optional[_Logging]:
        return self._Logging(self._config['logging'])
