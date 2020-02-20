# -*- coding: utf-8 -*-

import json
import logging
import logging.config
import os
from pathlib import Path, PurePath
from threading import Lock

from ...assets import DEFAULT_CONFIG
from ...meta import Singleton
from .arguments import _Arguments
from .browser import _Browser
from .logging import _Logging


class Config(metaclass=Singleton):
    '''Access and manage app configurations'''

    __io_lock = Lock()

    def __init__(self) -> None:
        self.load()

    def __exit___(self):
        logging.shutdown()

    @property
    def config_file(self) -> str:
        if not hasattr(self, '_config_file'):
            args_file = self.arguments.config
            fallback = str(Path(os.getcwd()) / 'Lightnovels' / 'config.json')
            setattr(self, '_config_file', args_file if args_file else fallback)
        return getattr(self, '_config_file')

    @property
    def work_directory(self) -> PurePath:
        return Path(self.config_file).parent

    def load(self, file_path: str = None) -> None:
        '''Loads config from a file'''
        if file_path is not None:
            setattr(self, '_config_file', file_path)
        try:
            # acquire io lock
            self.__io_lock.acquire()
            # reset config
            self.config = dict(DEFAULT_CONFIG)
            # read config from file
            with open(self.config_file, 'r', encoding='utf-8') as fp:
                config: dict = json.load(fp)
                self.config.update(config)
        except Exception:
            pass  # ignore errors
        finally:
            # release io lock
            self.__io_lock.release()
            # reset existing attributes
            self.__attrs__ = {}
            # initialize logger
            logging.config.dictConfig(self.config.get('logging', {}))

    def save(self) -> None:
        '''Saves config to a file'''
        try:
            # acquire io lock
            self.__io_lock.acquire()
            # create directory if not exists
            os.makedirs(self.work_directory, exist_ok=True)
            # save to file
            with open(self.config_file, 'w', encoding='utf-8') as fp:
                json.dump(self.config, fp, indent=2)
        except Exception:
            logging.exception('Fail to save config')
        finally:
            # release io lock
            self.__io_lock.release()

    # ========================================================================= #
    # Property declarations for easy access                                     #
    # ========================================================================= #

    def __resolve_attr(self, name: str, builder_func):
        if name not in self.__attrs__:
            self.__attrs__[name] = builder_func()
        return self.__attrs__.get(name)

    @property
    def arguments(self) -> _Arguments:
        return self.__resolve_attr('_arguments',
                                   lambda: _Arguments())

    @property
    def browser(self) -> _Browser:
        return self.__resolve_attr('_browser',
                                   lambda: _Browser(self, 'browser'))

    @property
    def logging(self) -> _Logging:
        return self.__resolve_attr('_logging',
                                   lambda: _Logging(self, 'logging'))
