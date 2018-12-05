import platform

isWindows = platform.system() == 'Windows'
isLinux = platform.system() == 'Linux'
isMac = platform.system() == 'Darwin'

class Icons:
    BOOK = '' if isWindows else '📒'
    CLOVER = '#' if isWindows else '🍀 '
    LINK = '-' if isWindows else '🔗'
    HANDS = '-' if isWindows else '🙏'
    SOUND = '<<' if isWindows else '🔊'
    RIGHT_ARROW = '->' if isWindows else '⮕'
    ERROR = '!' if isWindows else '❗'
    PARTY = '$' if isWindows else '📦'

    # --------------------------------------- #

    isWindows = isWindows
    isLinux = isLinux
    isMac = isMac
# end def
