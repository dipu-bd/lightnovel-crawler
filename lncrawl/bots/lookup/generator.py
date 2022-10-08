import os
from typing import Type

from colorama import Style

from ...assets.chars import Chars
from ...core.crawler import Crawler
from ...core.exeptions import LNException


def generate_crawler(
    template: Type[Crawler],
    output_file: str,
    classname: str,
    base_url: str,
    has_manga: bool,
    has_mtl: bool,
):
    if os.path.exists(output_file):
        raise LNException(f"File exists: {output_file}")

    lines = [
        "import logging",
        "",
        f"from {template.__module__} import {template.__name__}",
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "",
        f"class {classname}({template.__name__}):",
        f"    has_mtl = {bool(has_mtl)}",
        f"    has_manga = {bool(has_manga)}",
        f'    base_url = ["{base_url}"]',
        "",
    ]
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print()
    print(
        Style.BRIGHT + Chars.PARTY,
        "Generated source file",
        Chars.PARTY + Style.RESET_ALL,
    )
    print(Chars.RIGHT_ARROW, output_file)
    print()
