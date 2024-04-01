import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class Novelnextz(NovelFullTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://novelnextz.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tag_text_pairs.update(
            {
                "h4": [
                    r"Chapter \d+",
                    r"^\s*(Translator|Editor):.*$",
                ],
                "p": [
                    r"^\s*(Translator|Editor):.*$",
                    r"Bookmark this website \( ",
                    r"\)  to update the latest novels\.",
                ],
                "strong": r"NovelNext\.com",
            }
        )
