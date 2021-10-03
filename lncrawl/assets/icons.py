# -*- coding: utf-8 -*-
import platform

isMac = platform.system() == 'Darwin'
isLinux = platform.system() == 'Linux'
isWindows = platform.system() == 'Windows'


class Icons:
    isMac = isMac
    isLinux = isLinux
    isWindows = isWindows
    hasSupport = isLinux or isMac
    EOL = '\r\n' if isWindows else '\n'

    # --------------------------------------- #

    EMPTY = ' '
    BOOK = '📒' if hasSupport else '[#]'
    CLOVER = '🍀' if hasSupport else '*'
    LINK = '🔗' if hasSupport else '-'
    HANDS = '🙏' if hasSupport else '-'
    ERROR = '❗' if hasSupport else '!'
    PARTY = '📦' if hasSupport else '$'
    SOUND = '🔊' if hasSupport else '<<'
    SPARKLE = '✨' if hasSupport else '*'
    INFO = '💁' if hasSupport else '>'
    RIGHT_ARROW = '➡' if hasSupport else '->'
# end def
