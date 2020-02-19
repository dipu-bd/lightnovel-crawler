# -*- coding: utf-8 -*-
import json
import logging
import logging.config
import os
from pathlib import Path, PurePath
from threading import Lock
from typing import *

from ..assets import DEFAULT_CONFIG
from ..meta import Singleton
from .arguments import get_args


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
            fallback = str(Path(os.getcwd()) / 'Lightnovels' / 'config.json')
            setattr(self, '_config_file', self.arguments.config or fallback)
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
        except Exception as ex:
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

    class __Section__:
        def __init__(self, data: dict):
            self.__data__ = data

    class _Arguments(__Section__):
        def __init__(self):
            super().__init__(get_args().__dict__)

        @property
        def config(self):
            return self.__data__.get('config')

    class _Browser(__Section__):
        @property
        def concurrent_requests(self) -> int:
            return self.__data__.get('concurrent_requests', 5)

        @concurrent_requests.setter
        def concurrent_requests(self, value: int) -> None:
            self.__data__['concurrent_requests'] = value
            Config().save()

        @property
        def soup_parser(self) -> str:
            return self.__data__.get('soup_parser', 'html5lib')

        @soup_parser.setter
        def soup_parser(self, value: str) -> None:
            self.__data__['soup_parser'] = value
            Config().save()

        @property
        def response_timeout(self) -> Union[int, float, None]:
            return self.__data__.get('response_timeout', None)

        @response_timeout.setter
        def response_timeout(self, value: int) -> None:
            self.__data__['response_timeout'] = value
            Config().save()

        @property
        def stream_chunk_size(self) -> int:
            return self.__data__.get('stream_chunk_size', 10 * 1024)

        @stream_chunk_size.setter
        def stream_chunk_size(self, value: int) -> None:
            self.__data__['stream_chunk_size'] = value
            Config().save()

        @property
        def cloudscraper(self) -> dict:
            return self.__data__.get('cloudscraper', {})

    class _Logging(__Section__):
        @property
        def loggers(self) -> dict:
            return self.__data__.get('loggers', {})

        @property
        def handlers(self) -> dict:
            return self.__data__.get('handlers', {})

        @property
        def root_log_handlers(self) -> List[str]:
            return self.loggers.get('', {}).get('handlers', [])

        def add_root_log_handler(self, handler_name: str) -> None:
            loggers = dict(self.loggers)
            loggers.setdefault('', {})
            loggers[''].setdefault('handlers', [])
            loggers['']['handlers'].append(handler_name)
            self.__data__['loggers'] = loggers
            Config().save()

        def remove_root_log_handler(self, handler_name: str) -> None:
            loggers = dict(self.loggers)
            loggers.setdefault('', {})
            loggers[''].setdefault('handlers', [])
            loggers['']['handlers'].remove(handler_name)
            self.__data__['loggers'] = loggers
            Config().save()

        @property
        def root_log_level(self) -> str:
            return self.loggers.get('', {}).get('level', 'NOTSET')

        @root_log_level.setter
        def root_log_level(self, value: str) -> None:
            loggers = dict(self.loggers)
            loggers.setdefault('', {})
            loggers['']['level'] = value
            self.__data__['loggers'] = loggers
            Config().save()

    @property
    def arguments(self) -> _Arguments:
        return self.__resolve_attr('_arguments',
                                   lambda: self._Arguments())

    @property
    def browser(self) -> _Browser:
        return self.__resolve_attr('_browser',
                                   lambda: self._Browser(self.config['browser']))

    @property
    def logging(self) -> _Logging:
        return self.__resolve_attr('_logging',
                                   lambda: self._Logging(self.config['logging']))
