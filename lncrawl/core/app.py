import atexit
import logging
import os
import shutil
import zipfile
from pathlib import Path
from threading import Event
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from readability import Document  # type: ignore
from slugify import slugify

from .. import constants as C
from ..binders import generate_books
from ..core.exeptions import LNException
from ..core.sources import crawler_list, prepare_crawler
from ..models import Chapter, CombinedSearchResult, OutputFormat
from .browser import Browser
from .crawler import Crawler
from .download_chapters import fetch_chapter_body
from .download_images import fetch_chapter_images
from .exeptions import ScraperErrorGroup
from .metadata import save_metadata
from .novel_info import format_novel
from .novel_search import search_novels
from .scraper import Scraper
from .sources import rejected_sources

logger = logging.getLogger(__name__)


class App:
    """Bots are based on top of an instance of this app"""

    def __init__(self):
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
        self.generated_books: Dict[OutputFormat, List[str]] = {}
        self.generated_archives: Dict[OutputFormat, str] = {}
        self.archived_outputs = None
        self.good_file_name: str = ""
        self.no_suffix_after_filename = False
        self.search_progress: float = 0
        self.fetch_novel_progress: float = 0
        self.fetch_content_progress: float = 0
        self.fetch_images_progress: float = 0
        self.binding_progress: float = 0
        atexit.register(self.destroy)

    @property
    def progress(self):
        return (
            self.search_progress * 1
            + self.fetch_novel_progress * 0.05
            + self.fetch_content_progress * 0.45
            + self.fetch_images_progress * 0.45
            + self.binding_progress * 0.05
        )

    # ----------------------------------------------------------------------- #

    def destroy(self):
        atexit.unregister(self.destroy)
        if self.crawler:
            self.crawler.close()
            self.crawler = None
        self.chapters = []
        self.login_data = None
        self.book_cover = None
        self.search_progress = 0
        self.fetch_novel_progress = 0
        self.fetch_content_progress = 0
        self.fetch_images_progress = 0
        self.binding_progress = 0
        self.archived_outputs = None
        self.generated_books = {}
        self.generated_archives = {}
        logger.debug("DONE")

    # ----------------------------------------------------------------------- #

    def prepare_search(self):
        """Requires: user_input"""
        """Produces: [crawler, output_path] or [crawler_links]"""
        if not self.user_input:
            raise LNException("User input is not valid")

        if self.user_input.startswith("http"):
            logger.info("Detected URL input")
            crawler = prepare_crawler(self.user_input)
            if not self.crawler or self.crawler.home_url != crawler.home_url:
                self.crawler = crawler
        else:
            logger.info("Detected query input")
            self.crawler_links = [
                str(link)
                for link, crawler in crawler_list.items()
                if crawler.search_novel != Crawler.search_novel
                and link.startswith("http")
                and link not in rejected_sources
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

        self.fetch_novel_progress = 0
        self.fetch_content_progress = 0
        self.fetch_images_progress = 0
        self.binding_progress = 0

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
        self.search_progress = 0

        if not isinstance(self.crawler, Crawler):
            raise LNException("No crawler is selected")

        if self.can_do("login") and self.login_data:
            logger.debug("Login with %s", self.login_data)
            self.crawler.login(*list(self.login_data))

        self.fetch_novel_progress = 0
        self.crawler.read_novel_info()
        format_novel(self.crawler)
        self.fetch_novel_progress = 100

        if not len(self.crawler.chapters):
            raise Exception("No chapters found")
        if not len(self.crawler.volumes):
            raise Exception("No volumes found")

        self.prepare_novel_output_path()
        save_metadata(self)

    def prepare_novel_output_path(self):
        assert self.crawler

        if not self.good_file_name:
            self.good_file_name = slugify(
                self.crawler.novel_title,
                max_length=50,
                separator=" ",
                lowercase=False,
                word_boundary=True,
            )

        source_name = slugify(urlparse(self.crawler.novel_url).netloc)
        self.output_path = str(
            Path(C.DEFAULT_OUTPUT_PATH) / source_name / self.good_file_name
        )
        os.makedirs(self.output_path, exist_ok=True)

    # ----------------------------------------------------------------------- #

    def start_download(self, signal=Event()):
        """Requires: crawler, chapters, output_path"""
        if not self.output_path:
            raise LNException("Output path is not defined")
        if not Path(self.output_path).is_dir():
            raise LNException(f"Output path does not exists: ({self.output_path})")

        save_metadata(self)
        if signal.is_set():
            return  # cancelled

        fetch_chapter_body(self, signal)

        save_metadata(self)
        if signal.is_set():
            return  # cancelled

        fetch_chapter_images(self, signal)
        save_metadata(self, True)

        if self.crawler and self.can_do("logout"):
            self.crawler.logout()

    # ----------------------------------------------------------------------- #

    def bind_books(self):
        """Requires: crawler, chapters, output_path, pack_by_volume, book_cover, output_formats"""
        logger.info("Processing data for binding")
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
            data[f"c{first_id}-{last_id}"] = self.chapters

        self.generated_books = {}
        for fmt, file in generate_books(self, data):
            self.generated_books.setdefault(fmt, [])
            self.generated_books[fmt].append(file)
            save_metadata(self)

    # ----------------------------------------------------------------------- #

    def compress_books(self, archive_singles=False):
        logger.info("Compressing output...")

        output_path = Path(self.output_path)
        archive_path = output_path / 'archives'
        os.makedirs(archive_path, exist_ok=True)

        # Archive files
        self.archived_outputs = []
        self.generated_archives = {}
        for fmt, file_list in self.generated_books.items():
            if not file_list:
                logger.info(f"No files for {fmt}")
                continue

            first_file = Path(file_list[0])
            if (not archive_singles and len(file_list) == 1 and first_file.is_file()):
                logger.info(f"Not archiving single file for {fmt}")
                archive_file = archive_path / first_file.name
                shutil.copyfile(file_list[0], archive_file)
            else:
                output_name = f"{self.good_file_name} ({fmt}).zip"
                archive_file = archive_path / output_name
                logger.info(f"Compressing {len(file_list)} files")
                with zipfile.ZipFile(archive_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                    root_file = output_path / fmt
                    for file in file_list:
                        file_path = Path(file)
                        if file_path.is_relative_to(root_file):
                            arcname = file_path.relative_to(root_file).as_posix()
                        elif file_path.is_relative_to(output_path):
                            arcname = file_path.relative_to(output_path).as_posix()
                        else:
                            continue
                        zipf.write(file, arcname)

                logger.info("Compressed: %s", output_name)

            if archive_file:
                self.archived_outputs.append(str(archive_file))
                self.generated_archives[fmt] = str(archive_file)
                save_metadata(self)
