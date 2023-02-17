import atexit
import logging
import os
import shutil
from threading import Thread
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from readability import Document
from slugify import slugify

from .. import constants as C
from ..binders import available_formats, generate_books
from ..core.exeptions import LNException
from ..core.sources import crawler_list, prepare_crawler
from ..models import Chapter, CombinedSearchResult, OutputFormat
from .browser import Browser
from .crawler import Crawler
from .downloader import fetch_chapter_body, fetch_chapter_images
from .exeptions import ScraperErrorGroup
from .novel_info import format_novel, save_metadata
from .novel_search import search_novels
from .scraper import Scraper

logger = logging.getLogger(__name__)


class App:
    """Bots are based on top of an instance of this app"""

    def __init__(self):
        self.progress: float = 0
        self.user_input: Optional[str] = None
        self.crawler_links: List[str] = []
        self.crawler: Optional[Crawler] = None
        self.login_data: Optional[Tuple[str, str]] = None
        self.search_results: List[CombinedSearchResult] = []
        self.output_path = C.DEFAULT_OUTPUT_PATH
        self.pack_by_volume = False
        self.chapters: List[Chapter] = []
        self.book_cover: Optional[str] = None
        self.output_formats: Dict[OutputFormat, bool] = {}
        self.archived_outputs = None
        self.good_source_name: str = ""
        self.good_file_name: str = ""
        self.no_suffix_after_filename = False
        atexit.register(self.destroy)

    def __background(self, target_method, *args, **kwargs):
        t = Thread(target=target_method, args=args, kwargs=kwargs)
        t.start()
        while t.is_alive():
            t.join(1)

    # ----------------------------------------------------------------------- #

    def initialize(self):
        logger.info("Initialized App")

    def destroy(self):
        if self.crawler:
            self.crawler.__del__()
        self.chapters.clear()
        logger.info("App destroyed")

    # ----------------------------------------------------------------------- #

    def prepare_search(self):
        """Requires: user_input"""
        """Produces: [crawler, output_path] or [crawler_links]"""
        if not self.user_input:
            raise LNException("User input is not valid")

        if self.user_input.startswith("http"):
            logger.info("Detected URL input")
            self.crawler = prepare_crawler(self.user_input)
        else:
            logger.info("Detected query input")
            self.crawler_links = [
                str(link)
                for link, crawler in crawler_list.items()
                if crawler.search_novel != Crawler.search_novel
            ]

    def guess_novel_title(self, url: str) -> str:
        try:
            scraper = Scraper(url)
            response = scraper.get_response(url)
            reader = Document(response.text)
        except ScraperErrorGroup as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed to get response: %s", e)
            with Browser() as browser:
                browser.visit(url)
                browser.wait("body")
                reader = Document(browser.html)
        return reader.short_title()

    def search_novel(self):
        """Requires: user_input, crawler_links"""
        """Produces: search_results"""
        logger.info("Searching for novels in %d sites...", len(self.crawler_links))

        search_novels(self)

        if not self.search_results:
            raise LNException("No results for: %s" % self.user_input)

        logger.info(
            "Total %d novels found from %d sites",
            len(self.search_results),
            len(self.crawler_links),
        )

    # ----------------------------------------------------------------------- #

    def can_do(self, prop_name):
        if not hasattr(self.crawler.__class__, prop_name):
            return False
        if not hasattr(Crawler, prop_name):
            return True
        return getattr(self.crawler.__class__, prop_name) != getattr(Crawler, prop_name)

    def get_novel_info(self):
        """Requires: crawler, login_data"""
        """Produces: output_path"""
        if not isinstance(self.crawler, Crawler):
            raise LNException("No crawler is selected")

        if self.can_do("login") and self.login_data:
            logger.debug("Login with %s", self.login_data)
            self.crawler.login(*list(self.login_data))

        self.__background(self.crawler.read_novel_info)

        format_novel(self.crawler)
        if not len(self.crawler.chapters):
            raise Exception("No chapters found")
        if not len(self.crawler.volumes):
            raise Exception("No volumes found")

        if not self.good_file_name:
            self.good_file_name = slugify(
                self.crawler.novel_title,
                max_length=50,
                separator=" ",
                lowercase=False,
                word_boundary=True,
            )

        self.good_source_name = slugify(urlparse(self.crawler.home_url).netloc)
        self.output_path = os.path.join(
            C.DEFAULT_OUTPUT_PATH, self.good_source_name, self.good_file_name
        )

    # ----------------------------------------------------------------------- #

    def start_download(self):
        """Requires: crawler, chapters, output_path"""
        if not self.output_path or not os.path.isdir(self.output_path):
            raise LNException("Output path is not defined")

        assert self.crawler

        save_metadata(self)
        fetch_chapter_body(self)
        save_metadata(self)
        fetch_chapter_images(self)
        save_metadata(self, True)

        if not self.output_formats.get("json", False):
            shutil.rmtree(os.path.join(self.output_path, "json"), ignore_errors=True)

        if self.can_do("logout"):
            self.crawler.logout()

    # ----------------------------------------------------------------------- #

    def bind_books(self):
        """Requires: crawler, chapters, output_path, pack_by_volume, book_cover, output_formats"""
        logger.debug("Processing data for binding")
        assert self.crawler

        data = {}
        if self.pack_by_volume:
            for vol in self.crawler.volumes:
                # filename_suffix = 'Volume %d' % vol['id']
                filename_suffix = "Chapter %d-%d" % (
                    vol["start_chapter"],
                    vol["final_chapter"],
                )
                data[filename_suffix] = [
                    x
                    for x in self.chapters
                    if x["volume"] == vol["id"] and len(x["body"]) > 0
                ]

        else:
            first_id = self.chapters[0]["id"]
            last_id = self.chapters[-1]["id"]
            vol = "c%s-%s" % (first_id, last_id)
            data[vol] = self.chapters

        generate_books(self, data)

    # ----------------------------------------------------------------------- #

    def compress_books(self, archive_singles=False):
        logger.debug("Compressing output...")
        # Get which paths to be archived with their base names
        path_to_process = []

        for fmt in list({k: v for k, v in self.output_formats.items() if v == True}):
            root_dir = os.path.join(self.output_path, fmt)
            if os.path.isdir(root_dir):
                path_to_process.append(
                    [root_dir, self.good_file_name + " (" + fmt + ")"]
                )

        logger.debug("path_to_process: %s", path_to_process)

        # Archive files
        self.archived_outputs = []
        for root_dir, output_name in path_to_process:
            file_list = os.listdir(root_dir)
            logger.debug("file_list: %s", file_list)
            if len(file_list) == 0:
                logger.debug("It has no files: %s", root_dir)
                continue

            archived_file = None
            if (
                len(file_list) == 1
                and not archive_singles
                and not os.path.isdir(os.path.join(root_dir, file_list[0]))
            ):
                logger.debug("Not archiving single file inside %s" % root_dir)
                archived_file = os.path.join(root_dir, file_list[0])
            else:
                base_path = os.path.join(root_dir, output_name)
                logger.debug("Compressing %s to %s" % (root_dir, base_path))
                archived_file = shutil.make_archive(
                    base_path,
                    format="zip",
                    root_dir=root_dir,
                )
                logger.debug(f"Compressed: {os.path.basename(archived_file)}")

            if archived_file:
                logger.debug(
                    "appending archived file to archived_outputs: %s", archived_file
                )
                self.archived_outputs.append(archived_file)
