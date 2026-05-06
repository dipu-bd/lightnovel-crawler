import inspect
import logging
import os
from typing import Union

from rich.logging import RichHandler


class Logger:
    def __init__(self) -> None:
        self._level = logging.NOTSET
        self.progress_bar: bool = False

    @property
    def level(self) -> int:
        return self._level

    @property
    def is_debug(self) -> bool:
        return self.level == logging.DEBUG

    @property
    def is_info(self) -> bool:
        return self.is_debug or self.level == logging.INFO

    @property
    def is_warn(self) -> bool:
        return self.is_info or self.level == logging.WARN

    def setup(self, level: Union[int, str, None] = None) -> None:
        if level is None:
            level = int(os.getenv("LNCRAWL_LOG_LEVEL", "0"))
        if isinstance(level, int):
            levels = ["NOTSET", "WARN", "INFO", "DEBUG"]
            level = levels[max(0, min(level, 3))]
        if level:
            self._level = getattr(logging, level, logging.NOTSET)

        if self._level > 0:
            handler = RichHandler(
                level=self._level,
                tracebacks_show_locals=False,
                rich_tracebacks=True,
                markup=True,
            )
            logging.basicConfig(
                level=self._level,
                handlers=[handler],
                format="%(message)s",
                datefmt="[%X]",
                force=True,
            )
        self.progress_bar = not self.is_info

    def log(self, level: int, *args, **kwargs) -> None:
        stacklevel = kwargs.pop("stacklevel", 0) + 2
        frame = inspect.stack()[stacklevel]
        kwargs["stacklevel"] = stacklevel
        logger = logging.getLogger(frame.filename)
        logger.log(level, *args, **kwargs)

    def error(self, *args, **kwargs) -> None:
        self.log(logging.ERROR, *args, **kwargs, stacklevel=1)

    def warn(self, *args, **kwargs) -> None:
        self.log(logging.WARNING, *args, **kwargs, stacklevel=1)

    def info(self, *args, **kwargs) -> None:
        self.log(logging.INFO, *args, **kwargs, stacklevel=1)

    def debug(self, *args, **kwargs) -> None:
        self.log(logging.DEBUG, *args, **kwargs, stacklevel=1)
