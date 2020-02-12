# -*- coding: utf-8 -*-
import platform

from .version import get_value as get_version

isMac = platform.system() == 'Darwin'
isLinux = platform.system() == 'Linux'
isWindows = platform.system() == 'Windows'

APP_SHORT_NAME = 'lnc'
APP_FULL_NAME = 'lightnovel-crawler'
APP_VERSION = get_version()

CONSOLE_MAX_LINES = 80
try:
    _row, _ = os.get_terminal_size()
    if _row < CONSOLE_MAX_LINES:
        CONSOLE_MAX_LINES = _row
except Exception:
    pass
