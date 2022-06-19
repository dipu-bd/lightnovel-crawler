# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from lncrawl.core.app import App
from lncrawl.core.crawler import Crawler
import logging
from urllib.parse import urlparse
from slugify import slugify

logger = logging.getLogger(__name__)
from .. import lib


class JobHandler:
    def __init__(self, job_id):
        self.app = App()
        self.app.output_formats = {"json": True}
        self.job_id = job_id
        self.last_action = None
        self.last_activity = datetime.now()
        self.executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix=job_id)
        self.selected_novel = None
        self.is_busy = False
        self.search_results = None
        self.is_finished = False
        self.crashed = False

    # -----------------------------------------------------------------------------
    def crash(self, reason):
        self.crashed = True
        self.set_last_action(reason)
        logger.exception(reason)
        self.destroy()
        return reason

    def destroy(self):
        print("DESTROYING")
        self.executor.submit(self.destroy_sync)

    def destroy_sync(self):
        print("DESTROYING SYNC")
        try:
            print("REPLACEING APP")
            print(lib.jobs[self.job_id])
            lib.jobs[self.job_id] = lib.FinishedJob(
                (not self.crashed), self.last_action, self.last_activity
            )
            print(lib.jobs[self.job_id])

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

    def set_last_action(self, action):
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
    def get_list_of_novel(self, query):
        self.is_busy = True
        self.executor.submit(self._get_list_of_novel, query)

    def _get_list_of_novel(self, query):
        print(f"Getting list of novels for {query}")
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

    # -----------------------------------------------------------------------------

    def select_novel(self, novel_id):
        print(f"Novel selected: {novel_id}")
        self.selected_novel = self.app.search_results[novel_id]

    def get_list_of_sources(self):
        print(f"Getting list of sources for {self.selected_novel['title']}")
        self.set_last_action("Source selection")
        novel_list = self.selected_novel["novels"]

        return {
            "novel": self.selected_novel["title"],
            "found": len(novel_list),
            "content": [
                {
                    "id": i,
                    "url": item["url"],
                    "info": item["info"] if "info" in item else "",
                }
                for i, item in enumerate(novel_list)
            ],
        }

    def select_source(self, source_id):
        print(f"Source selected: {source_id}")
        self.is_busy = True

        self.set_last_action(f"Selected {self.selected_novel['novels'][source_id]}")
        self.app.prepare_crawler(self.selected_novel["novels"][source_id]["url"])

        self.set_last_action("Getting information about your novel...")
        self.executor.submit(self.download_novel_info)

    def download_novel_info(self):
        print(f"Downloading info for {self.selected_novel['title']}")
        self.is_busy = True
        self.set_last_action("Getting novel information...")

        try:
            self.app.get_novel_info()
        except Exception as ex:
            return self.crash(f"Failed to get novel info : {ex}")

        print(f"Novel info downloaded: {self.selected_novel['title']}")

        source_name = slugify(urlparse(self.app.crawler.home_url).netloc)
        output_path = lib.LIGHTNOVEL_FOLDER / self.app.good_file_name / source_name
        self.app.output_path = str(output_path)
        if not output_path.exists():
            output_path.mkdir(parents=True)
        print(f"Output path : {output_path}")

        self.is_busy = False

        # self.app.output_path

    # def select_range(self, start: int, finish: int):
    #     print(f"Selected range: {start -1} - {finish-1}")
    #     self.set_last_action("Set download range")
    #     self.app.chapters = self.app.crawler.chapters[start - 1 : finish - 1]

    def select_range(self):
        self.set_last_action("Set download range")
        self.app.chapters = self.app.crawler.chapters[:]

    def start_download(self):
        self.is_busy = True
        self.executor.submit(self._start_download)

    def _start_download(self):
        print(f"Starting download for {self.selected_novel['title']}")
        self.is_busy = True
        self.set_last_action("Downloading")

        self.app.pack_by_volume = False

        try:
            assert isinstance(self.app.crawler, Crawler)
            self.app.start_download()
            self.set_last_action("Compressing")
            self.app.compress_books()
            self.set_last_action("Finished downloading, destroying session")

        except Exception as ex:
            self.crash(f"Download failed : {ex}")

        novel_info = lib.get_novel_info(lib.LIGHTNOVEL_FOLDER / self.app.good_file_name)
        is_in_all_novels = False

        for downloaded in lib.all_downloaded_novels:
            if novel_info.title == downloaded.title:
                is_in_all_novels = True
                break

        if not is_in_all_novels:
            lib.all_downloaded_novels.append(novel_info)


        self.is_busy = False
        print("DESTROYING SESSION")
        self.destroy()
