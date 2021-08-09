# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlparse

from questionary import prompt

from ...core import display
from ...core.app import App
from ...core.arguments import get_args
from ...core.sources import rejected_sources
from .open_folder_prompt import display_open_folder
from .resume_download import resume_session

logger = logging.getLogger(__name__)


def start(self):
    from . import ConsoleBot
    if not isinstance(self, ConsoleBot):
        raise Exception('Unknown self: ' + type(self))

    args = get_args()
    if args.list_sources:
        display.url_supported_list()
        return
    # end if
    if 'resume' in args:
        resume_session()
        return
    # end if

    self.app = App()
    self.app.initialize()

    # Set filename if provided
    self.app.good_file_name = (args.filename or '').strip()
    self.app.no_append_after_filename = args.filename_only

    # Process user input
    self.app.user_input = self.get_novel_url()
    try:
        self.app.init_search()
    except Exception as e:
        logger.debug("Fail to init crawler. Error: %s", e)
        if self.app.user_input.startswith('http'):
            url = urlparse(self.app.user_input)
            url = '%s://%s/' % (url.scheme, url.hostname)
            if url in rejected_sources:
                display.url_rejected(rejected_sources[url])
                return
            # end if
        # end if
        display.url_not_recognized()
        return
    # end if

    # Search novel and initialize crawler
    if not self.app.crawler:
        self.app.crawler_links = self.get_crawlers_to_search()
        self.app.search_novel()

        novel_url = self.choose_a_novel()
        self.log.info('Selected novel: %s' % novel_url)
        self.app.init_crawler(novel_url)
    # end if

    if self.app.can_do('login'):
        self.app.login_data = self.get_login_info()
    # end if

    self.app.get_novel_info()

    self.app.output_path = self.get_output_path()
    self.app.chapters = self.process_chapter_range()

    self.app.output_formats = self.get_output_formats()
    self.app.pack_by_volume = self.should_pack_by_volume()

    self.app.start_download()
    self.app.bind_books()
    self.app.compress_books()

    self.app.destroy()
    display.app_complete()

    display_open_folder(self.app.output_path)
# end def


def process_chapter_range(self):
    chapters = []
    res = self.get_range_selection()

    args = get_args()
    if res == 'all':
        chapters = self.app.crawler.chapters[:]
    elif res == 'first':
        n = args.first or 10
        chapters = self.app.crawler.chapters[:n]
    elif res == 'last':
        n = args.last or 10
        chapters = self.app.crawler.chapters[-n:]
    elif res == 'page':
        start, stop = self.get_range_using_urls()
        chapters = self.app.crawler.chapters[start:(stop + 1)]
    elif res == 'range':
        start, stop = self.get_range_using_index()
        chapters = self.app.crawler.chapters[start:(stop + 1)]
    elif res == 'volumes':
        selected = self.get_range_from_volumes()
        chapters = [
            chap for chap in self.app.crawler.chapters
            if selected.count(chap['volume']) > 0
        ]
    elif res == 'chapters':
        selected = self.get_range_from_chapters()
        chapters = [
            chap for chap in self.app.crawler.chapters
            if selected.count(chap['id']) > 0
        ]
    # end if

    if len(chapters) == 0:
        raise Exception('No chapters to download')
    # end if

    self.log.debug('Selected chapters:')
    self.log.debug(chapters)
    if not args.suppress:
        answer = prompt([
            {
                'type': 'list',
                'name': 'continue',
                'message': '%d chapters selected' % len(chapters),
                'choices': [
                    'Continue',
                    'Change selection'
                ],
            }
        ])
        if answer['continue'] == 'Change selection':
            return self.process_chapter_range()
        # end if
    # end if

    self.log.info('%d chapters to be downloaded', len(chapters))
    return chapters
# end def
