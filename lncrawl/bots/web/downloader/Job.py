# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Optional, Union
from lncrawl.core.app import App
from lncrawl.core.crawler import Crawler
import logging
from urllib.parse import urlparse
from slugify import slugify
from pathlib import Path
logger = logging.getLogger(__name__)
from .. import lib
from .. import database
from .. import read_novel_info

class JobHandler:
    original_query: str = ""
    selected_novel = None
    is_busy = False
    search_results: Optional[dict[str, Union[int, str, List]]] = None
    crashed: bool = False
    last_action: str = "Created job"
    metadata_downloaded = False

    def __init__(self, job_id: str):
        self.app = App()
        self.app.output_formats = {"json": True}
        self.job_id = job_id
        self.last_activity = datetime.now()
        self.executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix=job_id)

    # -----------------------------------------------------------------------------
    def crash(self, reason: str):
        print(reason)
        self.crashed = True
        self.set_last_action(reason)
        logger.exception(reason)
        self.destroy()
        return reason

    def destroy(self):
        self.executor.submit(self.destroy_sync)

    def destroy_sync(self):
        try:
            database.jobs[self.job_id] = FinishedJob(
                (not self.crashed),
                self.last_action,
                self.last_activity,
                self.original_query,
            )

            self.app.destroy()
            self.executor.shutdown(wait=False)
        except Exception as e:
            print(f"Error while destroying: {e}")
            logger.exception(f"While destroying JobHandler : {e}")
        finally:
            logger.info("Session destroyed: %s", self.job_id)

    # -----------------------------------------------------------------------------

    def busy(self):
        return {"Error": f"Busy, {self.last_action} started at {self.last_activity}"}

    def set_last_action(self, action: str):
        print("starting action : ", action)
        self.last_action = action
        self.last_activity = datetime.now()

    def get_status(self):
        if not self.is_busy:
            return "No current task"

        elif self.last_action == "Downloading":
            return (
                f"Downloaded {self.app.progress} of {len(self.app.chapters)} chapters"
            )

        elif self.last_action == "Searching":
            return (
                f"Searched {self.app.progress} of {len(self.app.crawler_links)} sources"
            )

        else:
            return self.last_action

    # -----------------------------------------------------------------------------
    def get_list_of_novel(self, query: str) -> None:
        self.original_query = query
        self.is_busy = True
        self.executor.submit(self._get_list_of_novel, query)

    def _get_list_of_novel(self, query: str):
        if len(query) < 4:
            self.is_busy = False
            return

        self.app.user_input = query
        try:
            self.set_last_action("Preparing crawler")
            self.app.prepare_search()
        except Exception as e:
            return self.crash(f"Fail to init crawler : {e}")

        try:
            self.set_last_action("Searching")
            self.app.search_novel()
        except Exception as e:
            return self.crash(f"Fail to search novel : {e}")

        self.is_busy = False

        self.search_results = {
            "found": len(self.app.search_results),
            "content": [
                {
                    "id": i,
                    "title": item["title"],
                    "sources": len(item["novels"]),
                }
                for i, item in enumerate(self.app.search_results)
            ],
            "query": query,
        }

    def select_novel(self, novel_id: int) -> None:
        self.selected_novel = self.app.search_results[novel_id]

    # -----------------------------------------------------------------------------

    def get_list_of_sources(self):
        self.set_last_action("Source selection")

        assert self.selected_novel, "No novel selected"

        return {
            "novel": self.selected_novel["title"],
            "content": [
                {
                    "url": item["url"],
                    "info": item["info"] if "info" in item else "",
                }
                for item in self.selected_novel["novels"]
            ],
        }

    def select_source(self, source_id: int):
        self.is_busy = True

        assert self.selected_novel, "No novel selected"

        self.set_last_action(f"Selected {self.selected_novel['novels'][source_id]}")
        self.app.prepare_crawler(self.selected_novel["novels"][source_id]["url"])  # type: ignore

        self.set_last_action("Getting information about your novel...")
        self.executor.submit(self.download_novel_info)

    # -----------------------------------------------------------------------------

    def prepare_direct_download(self, url: str):
        self.original_query = url
        self.is_busy = True
        self.app.prepare_crawler(url)  # type: ignore
        self.executor.submit(self.download_novel_info)

    # -----------------------------------------------------------------------------
    def download_novel_info(self):
        self.is_busy = True
        self.set_last_action("Getting novel information...")

        try:
            self.app.get_novel_info()
        except Exception as ex:
            return self.crash(f"Failed to get novel info : {ex}")

        source_name = slugify(urlparse(self.app.crawler.home_url).netloc)  # type: ignore
        output_path = lib.LIGHTNOVEL_FOLDER / self.app.good_file_name / source_name
        self.app.output_path = str(output_path)
        if not output_path.exists():
            output_path.mkdir(parents=True)

        self.is_busy = False
        self.metadata_downloaded = True

    # def select_range(self, start: int, finish: int):
    #     print(f"Selected range: {start -1} - {finish-1}")
    #     self.set_last_action("Set download range")
    #     self.app.chapters = self.app.crawler.chapters[start - 1 : finish - 1]

    def _select_range(self):
        self.set_last_action("Set download range")
        self.app.chapters = self.app.crawler.chapters[:]  # type: ignore

    def start_download(self):
        self.is_busy = True
        self._select_range()
        self.executor.submit(self._start_download)

    def _start_download(self):
        self.is_busy = True
        self.set_last_action("Downloading")

        self.app.pack_by_volume = False

        try:
            assert isinstance(self.app.crawler, Crawler)
            self.app.start_download()
            self.set_last_action("Compressing")
            self.app.compress_books()
            self.set_last_action("Finished downloading")
            self.set_last_action("Updating website")
            self._update_website()
            self.set_last_action("Success, destroying session")

        except Exception as ex:
            self.crash(f"Download failed : {ex}")

        self.destroy()

    def _update_website(self):

        novel_info = read_novel_info.get_novel_info(Path(self.app.output_path).parent)

        is_in_all_novels = False
        for i, downloaded_info in enumerate(database.all_downloaded_novels):
            if downloaded_info == novel_info:
                novel_info.rank = downloaded_info.rank
                database.all_downloaded_novels[i] = novel_info
                is_in_all_novels = True
                break

        if not is_in_all_novels:
            novel_info.rank = len(database.all_downloaded_novels) + 1
            database.all_downloaded_novels.append(novel_info)




class FinishedJob:
    """
    Represent a successfully downloaded novel, or a failed download.
    Replace JobHandler in lib.jobs when JobHandler is destroyed
    """

    is_busy = False
    last_action = "Finished"

    def __init__(
        self, success: bool, message: str, end_date: datetime, original_query: str
    ):
        print(f"FinishedJob: {success}, {message}, {end_date}")
        self.original_query = original_query
        self.success = success
        self.message = message
        self.end_date = end_date

    def get_status(self):
        return self.message

    def destroy(self):
        pass