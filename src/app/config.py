# -*- coding: utf-8 -*-
import atexit
import json
import logging
import logging.config
import os
from pathlib import Path, PurePath
from typing import *

from ..assets import DEFAULT_CONFIG
from ..meta import Singleton
from .arguments import get_args

from threading import Lock


class Config(metaclass=Singleton):
    '''Access and manage app configurations'''

    __io_lock = Lock()

    def __init__(self) -> None:
        # Cleanup at exit
        atexit.register(self.close)

        # Load default configuration
        self.config = dict(DEFAULT_CONFIG)

        # Load configuration from file
        self.load()

        # Initialize logger
        logging.config.dictConfig(self.logging.section)

    def close(self):
        self.save()
        logging.shutdown()

    def load(self) -> None:
        '''Loads config from a file'''
        if not os.path.isfile(self.config_file):
            return
        with self.__io_lock:
            with open(self.config_file, mode='r', encoding='utf-8') as fp:
                config: dict = json.load(fp)
                self.config.update(config)

    def save(self) -> None:
        '''Saves config to a file'''
        with self.__io_lock:
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
        def work_directory(self) -> Path:
            fallback = str(Path(os.getcwd()) / 'Lightnovels')
            return Path(self.section.get('work_directory', fallback))

        @work_directory.setter
        def work_directory(self, value: Union[str, Path]) -> None:
            self.section['work_directory'] = os.path.abspath(str(value))
            delattr(Config(), '_config_file_')
            Config().save()

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

        @root_log_level.setter
        def root_log_level(self, value: str) -> None:
            self.loggers['']['level'] = value
            Config().save()

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
