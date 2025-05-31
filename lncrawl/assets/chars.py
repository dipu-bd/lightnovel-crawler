from ..utils.common import static_cached_property
from ..utils.platforms import Platform


class Chars:
    @static_cached_property
    @staticmethod
    def __supported():
        return Platform.linux or Platform.mac

    # --------------------------------------- #

    @static_cached_property
    @staticmethod
    def EOL() -> str:
        return "\r\n" if Platform.windows else "\n"

    @static_cached_property
    @staticmethod
    def EMPTY():
        return " "

    @static_cached_property
    @staticmethod
    def BOOK():
        return "📒" if Chars.__supported else "[#]"

    @static_cached_property
    @staticmethod
    def CLOVER():
        return "🍀" if Chars.__supported else "*"

    @static_cached_property
    @staticmethod
    def LINK():
        return "🔗" if Chars.__supported else "-"

    @static_cached_property
    @staticmethod
    def HANDS():
        return "🙏" if Chars.__supported else "-"

    @static_cached_property
    @staticmethod
    def ERROR():
        return "❗" if Chars.__supported else "!"

    @static_cached_property
    @staticmethod
    def PARTY():
        return "📦" if Chars.__supported else "$"

    @static_cached_property
    @staticmethod
    def SOUND():
        return "🔊" if Chars.__supported else "<<"

    @static_cached_property
    @staticmethod
    def SPARKLE():
        return "✨" if Chars.__supported else "*"

    @static_cached_property
    @staticmethod
    def INFO():
        return "💁" if Chars.__supported else ">"

    @static_cached_property
    @staticmethod
    def RIGHT_ARROW():
        return "➡" if Chars.__supported else "->"
