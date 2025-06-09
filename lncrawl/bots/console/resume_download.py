import logging
from typing import List, Optional

from questionary import prompt

from ... import constants as C
from ...core import display
from ...core.app import App
from ...core.arguments import get_args
from ...core.crawler import Crawler
from ...core.metadata import get_metadata_list, load_metadata
from ...models import MetaInfo
from .open_folder_prompt import display_open_folder

logger = logging.getLogger(__name__)


def resume_session():
    args = get_args()
    output_path = args.resume or C.DEFAULT_OUTPUT_PATH

    resumable_meta_data: List[MetaInfo] = [
        meta
        for meta in get_metadata_list(output_path)
        if meta.novel and meta.session and not meta.session.completed
    ]

    meta: Optional[MetaInfo] = None
    if len(resumable_meta_data) == 1:
        meta = resumable_meta_data[0]
    elif len(resumable_meta_data) > 1:
        answer = prompt(
            [
                {
                    "type": "list",
                    "name": "resume",
                    "message": "Which one do you want to resume?",
                    "choices": display.format_resume_choices(resumable_meta_data),
                }
            ]
        )
        index = answer["resume"]
        meta = resumable_meta_data[index]

    if not meta:
        print("No unfinished download to resume\n")
        display.app_complete()
        return

    app = App()
    load_metadata(app, meta)
    assert isinstance(app.crawler, Crawler)

    print("Resuming", app.crawler.novel_title)
    print("Output path:", app.output_path)

    app.crawler.initialize()

    if app.can_do("login") and app.login_data:
        logger.debug("Login with %s", app.login_data)
        app.crawler.login(*list(app.login_data))

    list(app.start_download())
    list(app.bind_books())

    app.destroy()
    display.app_complete()
    display_open_folder(app.output_path)
