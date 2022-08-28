from typing import Optional
from .Novel import NovelFromSource
from pathlib import Path
from . import database

def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude]
    )


def emoji_flag(country_code: str):
    country_code = country_code.upper()
    country_code = country_code.lower()
    if country_code == "en":
        return "🇬🇧"
    elif country_code == "fr":
        return "🇫🇷"
    elif country_code == "de":
        return "🇩🇪"
    elif country_code == "es":
        return "🇪🇸"
    elif country_code == "it":
        return "🇮🇹"
    elif country_code == "pt":
        return "🇵🇹"
    elif country_code == "ru":
        return "🇷🇺"
    elif country_code == "jp":
        return "🇯🇵"
    elif country_code == "cn":
        return "🇨🇳"
    elif country_code == "kr":
        return "🇰🇷"
    elif country_code == "tw":
        return "🇹🇼"
    elif country_code == "id":
        return "🇮🇩"
    elif country_code == "th":
        return "🇹🇭"
    elif country_code == "vn":
        return "🇻🇳"
        
    return chr(ord(country_code[0]) + 127397) + chr(ord(country_code[1]) + 127397)




def findSourceWithPath(novel_and_source_path: Path) -> Optional[NovelFromSource]:
    """
    Find the NovelFromSource object corresponding to the path
    """
    novel = None
    for n in database.all_downloaded_novels:
        if novel_and_source_path.parent == n.path:
            novel = n
            break
    if not novel:
        return None

    source = None
    for s in novel.sources:
        if novel_and_source_path == s.path:
            source = s
            break
    if not source:
        return None

    return source