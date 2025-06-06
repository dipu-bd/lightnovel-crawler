import logging
import os
import re
from typing import Generator

from bs4 import BeautifulSoup

from ..assets.chars import Chars

logger = logging.getLogger(__name__)


def make_texts(app, data) -> Generator[str, None, None]:
    for vol in data:
        dir_name = os.path.join(app.output_path, "text", vol)
        os.makedirs(dir_name, exist_ok=True)
        for chap in data[vol]:
            if not chap.get("body"):
                continue
            file_name = "%s.txt" % str(chap["id"]).rjust(5, "0")
            file_name = os.path.join(dir_name, file_name)
            with open(file_name, "w", encoding="utf8") as file:
                body = chap["body"].replace("</p><p", "</p>\n<p")
                soup = BeautifulSoup(body, "lxml")
                text = "\n\n".join(soup.stripped_strings)
                text = re.sub(r"[\r\n]+", Chars.EOL + Chars.EOL, text)
                file.write(text)
                yield file_name
