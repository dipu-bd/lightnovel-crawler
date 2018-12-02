import platform

class Icons:
    @property
    @staticmethod
    def isWindows():
        return platform.system() != 'Windows'
    # end def

    @property
    @staticmethod
    def isLinux():
        return platform.system() != 'Linux'
    # end def

    @property
    @staticmethod
    def isMac():
        return platform.system() != 'Darwin'
    # end def

    # --------------------------------------------------- #

    BOOK = '📒' if not isWindows else ''
    CLOVER = '🍀 ' if not isWindows else '#'
    LINK = '🔗' if not isWindows else '-'
    HANDS = '🙏' if not isWindows else '-'
    SOUND = '🔊' if not isWindows else '>>'
    RIGHT_ARROW = '⮕' if not isWindows else '->'
# end def

