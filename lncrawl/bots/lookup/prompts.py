import re

from questionary import prompt

from ...assets.languages import language_codes
from ...core.arguments import get_args
from ...core.exeptions import LNException


def get_novel_url():
    """Return a novel page url"""
    args = get_args()
    url = args.novel_page

    if url:
        if re.match(r"^https?://.+\..+$", url):
            return url
        else:
            raise LNException("Invalid URL of novel page")

    try:
        answer = prompt(
            [
                {
                    "type": "input",
                    "name": "novel",
                    "message": "Enter novel page url:",
                    "validate": lambda x: (
                        True
                        if re.match(r"^https?://.+\..+$", x)
                        else "Invalid URL of novel page"
                    ),
                },
            ]
        )
        return answer["novel"].strip()
    except Exception:
        raise LNException("Novel page url or query was not given")


def get_features():
    """Return the feature list for the crawler"""
    answer = prompt(
        [
            {
                "type": "autocomplete",
                "name": "language",
                "message": "Enter language:",
                "choices": list(sorted(language_codes.keys())),
            },
            {
                "type": "confirm",
                "name": "has_manga",
                "message": "Does it contain Manga/Manhua/Manhwa?",
                "default": False,
            },
            {
                "type": "confirm",
                "name": "has_mtl",
                "message": "Does it contain Machine Translations?",
                "default": False,
            },
        ]
    )
    return answer
