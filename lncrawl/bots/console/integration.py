import logging
from urllib.parse import urlparse

from questionary import prompt

from ...core import display
from ...core.app import App
from ...core.arguments import get_args
from ...core.crawler import Crawler
from ...core.exeptions import LNException
from ...core.sources import crawler_list, prepare_crawler, rejected_sources
from .open_folder_prompt import display_open_folder
from .resume_download import resume_session

logger = logging.getLogger(__name__)


def start(self):
    from . import ConsoleBot

    assert isinstance(self, ConsoleBot)

    args = get_args()
    if args.list_sources:
        display.url_supported_list()
        return

    if "resume" in args:
        resume_session()
        return

    self.app = App()
    self.app.initialize()

    # Set filename if provided
    self.app.good_file_name = (args.filename or "").strip()
    self.app.no_suffix_after_filename = args.filename_only

    # Process user input
    self.app.user_input = self.get_novel_url()
    if not self.app.user_input.startswith("http"):
        logger.info("Detected query input")
        search_links = [
            str(link)
            for link, crawler in crawler_list.items()
            if crawler.search_novel != Crawler.search_novel
        ]
        self.search_mode = True
    else:
        url = urlparse(self.app.user_input)
        url = "%s://%s/" % (url.scheme, url.hostname)
        if url in rejected_sources:
            display.url_rejected(rejected_sources[url])
            raise LNException("Fail to init crawler: %s is rejected", url)
        try:
            logger.info("Detected URL input")
            self.app.crawler = prepare_crawler(self.app.user_input)
            self.search_mode = False
        except Exception as e:
            display.url_not_recognized()
            logger.debug("Trying to find it in novelupdates", e)
            guess = self.app.guess_novel_title(self.app.user_input)
            display.guessed_url_for_novelupdates()
            self.app.user_input = self.confirm_guessed_novel(guess)
            search_links = ["https://www.novelupdates.com/"]
            self.search_mode = True

    # Search for novels
    if self.search_mode:
        self.app.crawler_links = self.get_crawlers_to_search(search_links)
        self.app.search_novel()

    def _download_novel():
        assert isinstance(self.app, App)

        if self.search_mode:
            novel_url = self.choose_a_novel()
            self.log.info("Selected novel: %s" % novel_url)
            self.app.crawler = prepare_crawler(novel_url)

        if self.app.can_do("login"):
            self.app.login_data = self.get_login_info()

        print("Retrieving novel info...")
        self.app.get_novel_info()
        display.display_novel_title(
            self.app.crawler.novel_title,
            len(self.app.crawler.volumes),
            len(self.app.crawler.chapters),
            self.app.crawler.novel_url,
        )

        self.app.output_path = self.get_output_path()
        self.app.chapters = self.process_chapter_range()

        self.app.output_formats = self.get_output_formats()
        self.app.pack_by_volume = self.should_pack_by_volume()

    while True:
        try:
            _download_novel()
            break
        except LNException as e:
            raise e
        except Exception as e:
            if not self.search_mode:
                raise e
            elif not self.confirm_retry():
                raise LNException("Cancelled by user")

    self.app.start_download()
    self.app.bind_books()
    self.app.compress_books()

    self.app.destroy()
    display.app_complete()

    display_open_folder(self.app.output_path)


def process_chapter_range(self, disable_args=False):
    chapters = []
    res = self.get_range_selection(disable_args)

    args = get_args()
    if res == "all":
        chapters = self.app.crawler.chapters[:]
    elif res == "first":
        n = args.first or 10
        chapters = self.app.crawler.chapters[:n]
    elif res == "last":
        n = args.last or 10
        chapters = self.app.crawler.chapters[-n:]
    elif res == "page":
        start, stop = self.get_range_using_urls(disable_args)
        chapters = self.app.crawler.chapters[start : (stop + 1)]
    elif res == "range":
        start, stop = self.get_range_using_index(disable_args)
        chapters = self.app.crawler.chapters[start : (stop + 1)]
    elif res == "volumes":
        selected = self.get_range_from_volumes(disable_args)
        chapters = [
            chap
            for chap in self.app.crawler.chapters
            if selected.count(chap["volume"]) > 0
        ]
    elif res == "chapters":
        selected = self.get_range_from_chapters(disable_args)
        chapters = [
            chap for chap in self.app.crawler.chapters if selected.count(chap["id"]) > 0
        ]

    if len(chapters) == 0:
        raise LNException("No chapters to download")

    self.log.debug("Selected chapters:")
    self.log.debug(chapters)
    if not args.suppress:
        answer = prompt(
            [
                {
                    "type": "list",
                    "name": "continue",
                    "message": "%d chapters selected" % len(chapters),
                    "choices": ["Continue", "Change selection"],
                }
            ]
        )
        if answer.get("continue", "") == "Change selection":
            return self.process_chapter_range(True)

    self.log.info("%d chapters to be downloaded", len(chapters))
    return chapters
