import re
from typing import List

from questionary import prompt

from ...core import display
from ...core.arguments import get_args
from ...core.exeptions import LNException


def get_novel_url(self):
    """Returns a novel page url or a query"""
    args = get_args()
    if args.query and len(args.query) > 1:
        return args.query

    url = args.novel_page
    if url:
        if re.match(r"^https?://.+\..+$", url):
            return url
        else:
            raise LNException("Invalid URL of novel page")

    try:
        if args.suppress:
            raise LNException()

        answer = prompt(
            [
                {
                    "type": "input",
                    "name": "novel",
                    "message": "Enter novel page url or query novel:",
                    "validate": lambda a: True if a else "Input should not be empty",
                },
            ]
        )
        return answer["novel"].strip()
    except Exception:
        raise LNException("Novel page url or query was not given")


def get_crawlers_to_search(self) -> List[str]:
    """Returns user choice to search the choosen sites for a novel"""
    links = self.app.crawler_links
    if not links:
        return []

    args = get_args()
    if args.suppress or "sources" not in args:
        return links

    if args.sources:
        links = [link for link in links if re.search(args.sources, link)]

    if args.suppress or len(links) <= 1:
        return links

    answer = prompt(
        [
            {
                "type": "checkbox",
                "name": "sites",
                "message": "Where to search?",
                "choices": [{"name": x, "checked": True} for x in sorted(links)],
            }
        ]
    )

    selected = answer["sites"]
    return selected if len(selected) > 0 else links


def choose_a_novel(self):
    """Choose a single novel url from the search result"""
    args = get_args()

    # Choose a novel title
    choices = self.app.search_results
    selected_choice = self.app.search_results[0]
    if len(choices) > 1 and not args.suppress:
        answer = prompt(
            [
                {
                    "type": "list",
                    "name": "novel",
                    "message": "Which one is your novel?",
                    "choices": display.format_novel_choices(choices),
                }
            ]
        )

        index = int(answer["novel"].split(".")[0])
        selected_choice = self.app.search_results[index - 1]

    # Choose the novel source
    novels = selected_choice["novels"]
    selected_novel = novels[0]
    if len(novels) > 1 and not args.suppress:
        answer = prompt(
            [
                {
                    "type": "list",
                    "name": "novel",
                    "message": "Choose a source to download?",
                    "choices": ["0. Back"] + display.format_source_choices(novels),
                }
            ]
        )

        index = int(answer["novel"].split(".")[0])
        if index == 0:
            return self.choose_a_novel()

        selected_novel = novels[index - 1]

    return selected_novel["url"]


def confirm_retry(self) -> bool:
    """Returns whether to retry on failure"""
    args = get_args()

    if args.suppress:
        return False

    answer = prompt(
        [
            {
                "type": "confirm",
                "name": "retry",
                "message": "Do you want to choose another novel?",
                "default": True,
            },
        ]
    )

    return answer.get("retry")
