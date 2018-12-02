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

    BOOK = '📒' if isWindows else ''
    CLOVER = '🍀 ' if isWindows else '#'
    LINK = '🔗' if isWindows else '-'
    HANDS = '🙏' if isWindows else '-'
    SOUND = '🔊' if isWindows else '>>'
    RIGHT_ARROW = '⮕' if isWindows else '->'
# end def

