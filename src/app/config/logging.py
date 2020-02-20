# -*- coding: utf-8 -*-

from typing import List

from .section import __Section__


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
        self.save()

    def remove_root_log_handler(self, handler_name: str) -> None:
        loggers = dict(self.loggers)
        loggers.setdefault('', {})
        loggers[''].setdefault('handlers', [])
        loggers['']['handlers'].remove(handler_name)
        self.__data__['loggers'] = loggers
        self.save()

    @property
    def root_log_level(self) -> str:
        return self.loggers.get('', {}).get('level', 'NOTSET')

    @root_log_level.setter
    def root_log_level(self, value: str) -> None:
        loggers = dict(self.loggers)
        loggers.setdefault('', {})
        loggers['']['level'] = value
        self.__data__['loggers'] = loggers
        self.save()
