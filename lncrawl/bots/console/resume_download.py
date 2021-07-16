# -*- coding: utf-8 -*-
import json
import logging
from pathlib import Path

from questionary import prompt

from ... import constants as C
from ...core import display
from ...core.app import App
from ...core.arguments import get_args
from ...core.crawler import Crawler
from .open_folder_prompt import display_open_folder

logger = logging.getLogger(__name__)


def resume_session():
    args = get_args()
    output_path = args.resume or C.DEFAULT_OUTPUT_PATH

    resumable_meta_data = []
    for meta_file in Path(output_path).glob('**/' + C.META_FILE_NAME):
        with open(meta_file, 'r', encoding="utf-8") as file:
            data = json.load(file)
            if 'session' in data and not data['session']['completed']:
                resumable_meta_data.append(data)
            # end if
        # end with
    # end for

    metadata = None
    if len(resumable_meta_data) == 1:
        metadata = resumable_meta_data[0]
    elif len(resumable_meta_data) > 1:
        answer = prompt([
            {
                'type': 'list',
                'name': 'resume',
                'message': 'Which one do you want to resume?',
                'choices': display.format_resume_choices(resumable_meta_data),
            }
        ])
        index = int(answer['resume'].split('.')[0])
        metadata = resumable_meta_data[index - 1]
    # end if

    if not metadata:
        print('No unfinished download to resume\n')
        display.app_complete()
        return
    # end if

    app = load_session_from_metadata(metadata)
    print('Resuming', app.crawler.novel_title)
    print('Output path:', app.output_path)

    app.initialize()
    app.crawler.initialize()

    if app.can_do('login') and app.login_data:
        logger.debug('Login with %s', app.login_data)
        app.crawler.login(*list(app.login_data))
    # end if

    app.start_download()
    app.bind_books()
    app.compress_books()
    app.destroy()
    display.app_complete()
    display_open_folder(app.output_path)
# end def


def load_session_from_metadata(data) -> App:
    app = App()

    session_data = data['session']
    app.output_path = session_data['output_path']
    app.user_input = session_data['user_input']
    app.login_data = session_data['login_data']
    app.pack_by_volume = session_data['pack_by_volume']
    app.output_formats = session_data['output_formats']
    app.good_file_name = session_data['good_file_name']
    app.no_append_after_filename = session_data['no_append_after_filename']

    logger.info('Novel Url: %s', data['url'])
    app.init_crawler(data['url'])
    if not isinstance(app.crawler, Crawler):
        raise Exception('No crawler found for ' + data['url'])

    app.crawler.novel_title = data['title']
    app.crawler.novel_author = data['author']
    app.crawler.novel_cover = data['cover']
    app.crawler.volumes = data['volumes']
    app.crawler.chapters = data['chapters']
    app.crawler.is_rtl = data['rtl']

    app.chapters = [
        chap for chap in data['chapters']
        if chap['id'] in session_data['download_chapters']
    ]
    logger.info('Number of chapters to download: %d', len(app.chapters))
    logger.debug(app.chapters)

    return app
# end def
