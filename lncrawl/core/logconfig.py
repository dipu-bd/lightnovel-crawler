import atexit
import logging
import logging.config
import os

import urllib3
from colorama import Fore

from .arguments import get_args
from .display import debug_mode


def configure_logging():
    args = get_args()

    levels = ["NOTSET", "WARN", "INFO", "DEBUG"]
    level = os.getenv("LOG_LEVEL", levels[args.log or 0])
    log_file = os.getenv("LOG_FILE", args.log_file or "")

    os.environ["LOG_LEVEL"] = level
    os.environ["LOG_FILE"] = log_file

    if level == "NOTSET" and not log_file:
        urllib3.disable_warnings()
        return

    if level != "NOTSET":
        debug_mode(level)
        os.environ["debug_mode"] = "yes"
        atexit.register(logging.shutdown)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "file": {
                "format": "%(asctime)s [%(process)d]{%(thread)d} %(levelname)s %(filename)s:%(funcName)s:%(lineno)d\n(%(name)s) %(message)s\n",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "console": {
                "format": f"{Fore.CYAN}%(asctime)s {Fore.RED}[%(levelname)s] {Fore.YELLOW}(%(name)s)\n{Fore.WHITE}%(message)s{Fore.RESET}",
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "stream": "ext://sys.stdout",  # default is stderr
                "level": 1000,
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "file",
                "mode": "w",
                "encoding": "utf-8",
                "filename": log_file,
                "level": logging.DEBUG,
            },
        },
        "root": {  # root logger
            "level": logging.NOTSET,
            "handlers": ["file", "console"],
        },
    }
    if not log_file:
        del config["handlers"]["file"]
        config["root"]["level"] = logging.getLevelName(level)
        config["root"]["handlers"] = ["console"]
        config["handlers"]["console"]["level"] = logging.getLevelName(level)

    logging.config.dictConfig(config)
