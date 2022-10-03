from ..utils.platforms import Platform


class Chars:
    __supported = Platform.linux or Platform.mac

    # --------------------------------------- #

    EOL = "\r\n" if Platform.windows else "\n"
    EMPTY = " "
    BOOK = "📒" if __supported else "[#]"
    CLOVER = "🍀" if __supported else "*"
    LINK = "🔗" if __supported else "-"
    HANDS = "🙏" if __supported else "-"
    ERROR = "❗" if __supported else "!"
    PARTY = "📦" if __supported else "$"
    SOUND = "🔊" if __supported else "<<"
    SPARKLE = "✨" if __supported else "*"
    INFO = "💁" if __supported else ">"
    RIGHT_ARROW = "➡" if __supported else "->"
