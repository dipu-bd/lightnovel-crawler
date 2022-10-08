import logging
import os
import textwrap
from typing import Type

from colorama import Fore, Style

from ...assets.chars import Chars
from ...core.crawler import Crawler
from ...core.display import LINE_SIZE
from ...core.exeptions import LNException
from ...core.novel_info import format_novel
from ...core.sources import crawler_list, rejected_sources, template_list

logger = logging.getLogger(__name__)


def analyze_url(base_url: str, url: str) -> Type[Crawler]:
    if base_url in rejected_sources:
        raise LNException(f"Source is rejected. Reason: {rejected_sources[base_url]}")

    CrawlerType = crawler_list.get(base_url)
    if CrawlerType:
        raise LNException("A crawler already exists for this url")

    for index, template in enumerate(template_list):
        name = template.__name__
        print(Style.BRIGHT + Chars.CLOVER, "Checking", name, end=" ")
        print(f"[{index + 1} of {len(template_list)}]", Style.RESET_ALL)

        # To disable tqdm
        debug_mode = os.getenv("debug_mode")
        os.environ["debug_mode"] = "yes"
        try:
            print(" ", Chars.RIGHT_ARROW, "Create instance", end=" ")
            template.base_url = [base_url]
            template.is_template = False
            crawler = template()
            print(":", Fore.GREEN + "success" + Fore.RESET)

            print(" ", Chars.RIGHT_ARROW, "initialize()", end=" ")
            crawler.home_url = base_url
            crawler.initialize()
            print(":", Fore.GREEN + "success" + Fore.RESET)

            print(" ", Chars.RIGHT_ARROW, "read_novel_info()", end=" ")
            crawler.novel_url = url
            crawler.read_novel_info()
            format_novel(crawler)
            assert crawler.volumes, "Volumes not found"
            assert crawler.chapters, "Chapters not found"
            print(":", Fore.GREEN + "success" + Fore.RESET)

            print(" ", Chars.RIGHT_ARROW, "download_chapter_body()", end=" ")
            chapter = crawler.chapters[-1]
            body = crawler.download_chapter_body(chapter)
            assert body, "Chapter body not found"
            print(":", Fore.GREEN + "success" + Fore.RESET)

            return template
        except Exception as e:
            message = "\n".join(
                textwrap.wrap(
                    str(e),
                    width=LINE_SIZE,
                    initial_indent=(" " * 4),
                    subsequent_indent=(" " * 4),
                    drop_whitespace=True,
                    break_long_words=True,
                )
            )
            print(":", Fore.RED + "failed" + Fore.RESET)
            print(Style.DIM + message + Style.RESET_ALL)
        finally:
            print()
            if not debug_mode:
                os.environ.pop("debug_mode")

    raise LNException("No template match found for the url")
