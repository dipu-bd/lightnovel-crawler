import asyncio
import os
import random
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional

import discord

from lncrawl.core.app import App
from lncrawl.core.crawler import Crawler
from lncrawl.core.sources import prepare_crawler
from lncrawl.utils.uploader import upload

from .config import available_formats, disable_search, logger


class MessageHandler:
    def __init__(self, uid, client):
        self.app = App()
        self.uid = uid
        self.client = client
        self.state = None
        self.last_activity = datetime.now()
        self.closed = False
        self.get_current_status = None
        self.selected_novel: Optional[dict] = None
        self.executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix=uid)

    def process(self, message):
        self.last_activity = datetime.now()
        self.executor.submit(self.handle_message, message)

    def destroy(self):
        # self.send_sync('Closing current session')
        self.executor.submit(self.destroy_sync)

    def destroy_sync(self):
        try:
            self.get_current_status = None
            self.client.handlers.pop(self.uid)
            self.app.destroy()
            shutil.rmtree(self.app.output_path, ignore_errors=True)
            self.executor.shutdown(wait=False)
        except Exception:
            logger.exception("While destroying MessageHandler")
        finally:
            self.closed = True
            logger.info("Session destroyed: %s", self.uid)

    def handle_message(self, message: discord.Message):
        self.message = message
        self.user = message.author
        if not self.state:
            self.state = self.get_novel_url

        try:
            self.state()
        except Exception as ex:
            logger.exception("Failed to process state")
            self.send_sync("Something went wrong!\n`%s`" % str(ex))
            self.destroy()

    def is_busy(self) -> bool:
        return self.state == self.busy_state

    # ---------------------------------------------------------------------- #

    def wait_for(self, async_coroutine):
        asyncio.run_coroutine_threadsafe(async_coroutine, self.client.loop).result(
            timeout=3 * 60
        )

    async def send(self, *contents):
        if self.closed:
            return
        self.last_activity = datetime.now()
        async with self.user.typing():
            for text in contents:
                if not text:
                    continue

                await self.user.send(text)

    def send_sync(self, *contents):
        self.wait_for(self.send(*contents))

    def busy_state(self):
        text = self.message.content.strip()

        if text == "!cancel":
            self.destroy()
            return

        status = None
        if callable(self.get_current_status):
            status = self.get_current_status()

        if not status:
            status = random.choice(
                [
                    "Send !cancel to stop this session.",
                    "Please wait...",
                    "Processing, give me more time...",
                    "A little bit longer...",
                ]
            )

        self.send_sync(status)

    # ---------------------------------------------------------------------- #

    def get_novel_url(self):
        self.state = self.busy_state
        if disable_search:
            self.send_sync("Send me an URL of novel info page with chapter list!")
        else:
            self.send_sync(
                "I recognize these two categories:\n"
                "- Profile page url of a lightnovel.\n"
                "- A query to search your lightnovel.",
                "What are you looking for?",
            )

        self.state = self.handle_novel_url

    def handle_novel_url(self):
        self.state = self.busy_state

        text = self.message.content.strip()
        if text == "!cancel":
            self.destroy()
            return

        try:
            self.app.user_input = self.message.content.strip()
            self.app.prepare_search()
        except Exception:
            logger.exception("Fail to init crawler")
            self.send_sync(
                "\n".join(
                    [
                        "Sorry! I do not recognize this sources yet.",
                        "See list of supported sources here:",
                        "https://github.com/dipu-bd/lightnovel-crawler#c3-supported-sources",
                        "",
                        "You can send the novelupdates link of the novel too.",
                    ]
                )
            )
            self.get_novel_url()

        if self.app.crawler:
            self.send_sync("Got your page link")
            self.get_novel_info()
        elif self.app.user_input and len(self.app.user_input) < 4:
            self.send_sync("Your query is too short")
            self.state = self.handle_novel_url
            self.get_novel_url()
        else:
            if disable_search:
                self.send_sync(
                    "Sorry! I can not do searching.\n"
                    "Please use Google to find your novel first"
                )
                self.get_novel_url()
            else:
                self.send_sync(
                    'Searching %d sources for "%s"\n'
                    % (len(self.app.crawler_links), self.app.user_input),
                )
                self.display_novel_selection()

    # ------------------------------------------------------------ #
    # SEARCHING -- skips if DISCORD_DISABLE_SEARCH is 'true'
    # ------------------------------------------------------------ #

    def get_novel_selection_progres(self):
        return "Searched %d of %d sources" % (
            self.app.progress,
            len(self.app.crawler_links),
        )

    def display_novel_selection(self):
        self.get_current_status = self.get_novel_selection_progres
        self.app.search_novel()
        self.get_current_status = None
        if self.closed:
            return

        if len(self.app.search_results) == 0:
            self.send_sync('No novels found for "%s"' % self.app.user_input)
            self.state = self.handle_novel_url
        elif len(self.app.search_results) == 1:
            self.selected_novel = self.app.search_results[0]
            self.display_sources_selection()
        else:
            self.send_sync(
                "\n".join(
                    ["Found %d novels:" % len(self.app.search_results)]
                    + [
                        "%d. **%s** `%d sources`"
                        % (i + 1, item["title"], len(item["novels"]))
                        for i, item in enumerate(self.app.search_results)
                    ]
                    + [
                        "",
                        "Enter name or index of your novel.",
                        "Send `!cancel` to stop this session.",
                    ]
                )
            )
            self.state = self.handle_novel_selection

    def handle_novel_selection(self):
        self.state = self.busy_state

        text = self.message.content.strip()
        if text.startswith("!cancel"):
            self.get_novel_url()
            return

        match_count = 0
        selected = None
        for i, res in enumerate(self.app.search_results):
            if str(i + 1) == text:
                selected = res
                match_count += 1
            elif text.isdigit() or len(text) < 3:
                pass
            elif res["title"].lower().find(text) != -1:
                selected = res
                match_count += 1

        if match_count != 1:
            self.send_sync(
                "Sorry! You should select *one* novel from the list (%d selected)."
                % match_count
            )
            self.display_novel_selection()
            return

        self.selected_novel = selected
        self.display_sources_selection()

    def display_sources_selection(self):
        assert isinstance(self.selected_novel, dict)
        novel_list = self.selected_novel["novels"]
        self.send_sync(
            "**%s** is found in %d sources:\n"
            % (self.selected_novel["title"], len(novel_list))
        )

        for j in range(0, len(novel_list), 10):
            self.send_sync(
                "\n".join(
                    [
                        "%d. <%s> %s"
                        % (
                            (j + i + 1),
                            item["url"],
                            item["info"] if "info" in item else "",
                        )
                        for i, item in enumerate(novel_list[j : j + 10])
                    ]
                )
            )

        self.send_sync(
            "\n".join(
                [
                    "",
                    "Enter index or name of your source.",
                    "Send `!cancel` to stop this session.",
                ]
            )
        )
        self.state = self.handle_sources_to_search

    def handle_sources_to_search(self):
        self.state = self.busy_state

        assert isinstance(self.selected_novel, dict)
        if len(self.selected_novel["novels"]) == 1:
            novel = self.selected_novel["novels"][0]
            return self.handle_search_result(novel)

        text = self.message.content.strip()
        if text.startswith("!cancel"):
            return self.get_novel_url()

        match_count = 0
        selected = None
        for i, res in enumerate(self.selected_novel["novels"]):
            if str(i + 1) == text:
                selected = res
                match_count += 1
            elif text.isdigit() or len(text) < 3:
                pass
            elif res["url"].lower().find(text) != -1:
                selected = res
                match_count += 1

        if match_count != 1:
            self.send_sync(
                "Sorry! You should select *one* source "
                "from the list (%d selected)." % match_count
            )
            return self.display_sources_selection()

        self.handle_search_result(selected)

    def handle_search_result(self, novel):
        self.send_sync("Selected: %s" % novel["url"])
        self.app.crawler = prepare_crawler(novel["url"])
        self.get_novel_info()

    # ---------------------------------------------------------------------- #

    def get_novel_info(self):
        # TODO: Handle login here

        self.send_sync("Getting information about your novel...")
        self.executor.submit(self.download_novel_info)

    def download_novel_info(self):
        self.state = self.busy_state
        try:
            self.get_current_status = lambda: "Getting novel information..."
            self.app.get_novel_info()
            if self.closed:
                return
        except Exception as ex:
            logger.exception("Failed to get novel info")
            self.send_sync("Failed to get novel info.\n`%s`" % str(ex))
            self.destroy()
            return

        # Setup output path
        root = os.path.abspath(".discord_bot_output")
        good_name = os.path.basename(self.app.output_path)
        output_path = os.path.join(root, str(self.user.id), good_name)
        shutil.rmtree(output_path, ignore_errors=True)

        os.makedirs(output_path, exist_ok=True)
        self.app.output_path = output_path

        self.display_range_selection()

    def display_range_selection(self):
        self.send_sync(
            "\n".join(
                [
                    "Now you choose what to download:",
                    "- Send `!cancel` to stop this session.",
                    "- Send `all` to download all chapters",
                    "- Send `last 20` to download last 20 chapters. Choose any number you want.",
                    "- Send `first 10` for first 10 chapters. Choose any number you want.",
                    "- Send `volume 2 5` to download download volume 2 and 5. Pass as many numbers you need.",
                    "- Send `chapter 110 120` to download chapter 110 to 120. Only two numbers are accepted.",
                ]
            )
        )
        assert isinstance(self.app.crawler, Crawler)
        self.send_sync(
            "**It has `%d` volumes and `%d` chapters.**"
            % (len(self.app.crawler.volumes), len(self.app.crawler.chapters))
        )
        self.state = self.handle_range_selection

    def handle_range_selection(self):
        self.state = self.busy_state
        text = self.message.content.strip().lower()
        if text == "!cancel":
            self.destroy()
            return

        assert isinstance(self.app.crawler, Crawler)
        if text == "all":
            self.app.chapters = self.app.crawler.chapters[:]
        elif re.match(r"^first(\s\d+)?$", text):
            text = text[len("first") :].strip()
            n = int(text) if text.isdigit() else 50
            n = 50 if n < 0 else n
            self.app.chapters = self.app.crawler.chapters[:n]
        elif re.match(r"^last(\s\d+)?$", text):
            text = text[len("last") :].strip()
            n = int(text) if text.isdigit() else 50
            n = 50 if n < 0 else n
            self.app.chapters = self.app.crawler.chapters[-n:]
        elif re.match(r"^volume(\s\d+)+$", text):
            text = text[len("volume") :].strip()
            selected = re.findall(r"\d+", text)
            self.send_sync(
                "Selected volumes: " + ", ".join(selected),
            )
            selected = [int(x) for x in selected]
            self.app.chapters = [
                chap
                for chap in self.app.crawler.chapters
                if selected.count(chap["volume"]) > 0
            ]
        elif re.match(r"^chapter(\s\d+)+$", text):
            text = text[len("chapter") :].strip()
            pair = text.split(" ")
            if len(pair) == 2:

                def resolve_chapter(name):
                    cid = 0
                    if name.isdigit():
                        cid = int(name)
                    elif isinstance(self.app.crawler, Crawler):
                        cid = self.app.crawler.index_of_chapter(name)

                    return cid - 1

                first = resolve_chapter(pair[0])
                second = resolve_chapter(pair[1])
                if first > second:
                    second, first = first, second

                if first >= 0 or second < len(self.app.crawler.chapters):
                    self.app.chapters = self.app.crawler.chapters[first:second]

            if len(self.app.chapters) == 0:
                self.send_sync("Chapter range is not valid. Please try again")
                self.state = self.handle_range_selection
                return

        else:
            self.send_sync("Sorry! I did not recognize your input. Please try again")
            self.state = self.handle_range_selection
            return

        if len(self.app.chapters) == 0:
            self.send_sync(
                "You have not selected any chapters. Please select at least one"
            )
            self.state = self.handle_range_selection
            return

        self.send_sync("Got your range selection")
        self.display_output_selection()

    def display_output_selection(self):
        self.state = self.busy_state
        self.send_sync(
            "\n".join(
                [
                    "Now you can choose book formats to download:",
                    "- Send `!cancel` to stop.",
                    "- Send `!all` to download all formats _(it may take a very long time!)_",
                    "To select specific output formats:",
                    "- Send `pdf` to download only pdf format",
                    "- Send `epub pdf` to download both epub and pdf formats.",
                    "- Send `{space separated format names}` for multiple formats",
                    "Available formats: `" + "` `".join(available_formats) + "`",
                ]
            )
        )
        self.state = self.handle_output_selection

    def handle_output_selection(self):
        self.state = self.busy_state

        text = self.message.content.strip()
        if text.startswith("!cancel"):
            self.get_novel_url()
            return

        if text == "!all":
            output_format = set(available_formats)
        else:
            output_format = set(re.findall("|".join(available_formats), text.lower()))

        if not len(output_format):
            self.send_sync(
                "Sorry! I did not recognize your input. "
                "Try one of these: `" + "` `".join(available_formats) + "`"
            )
            self.state = self.handle_output_selection
            return

        self.app.output_formats = {x: (x in output_format) for x in available_formats}
        self.send_sync(
            "I will generate e-book in (%s) format" % (", ".join(output_format))
        )

        self.send_sync(
            "\n".join(
                [
                    "Starting download...",
                    "Send anything to view status.",
                    "Send `!cancel` to stop it.",
                ]
            )
        )

        self.executor.submit(self.start_download)

    # ---------------------------------------------------------------------- #

    def get_download_progress_status(self):
        return "Downloaded %d of %d chapters" % (
            self.app.progress,
            len(self.app.chapters),
        )

    def start_download(self):
        self.app.pack_by_volume = False

        try:
            assert isinstance(self.app.crawler, Crawler)
            self.send_sync(
                "**%s**" % self.app.crawler.novel_title,
                "Downloading %d chapters..." % len(self.app.chapters),
            )
            self.get_current_status = self.get_download_progress_status
            self.app.start_download()
            self.get_current_status = None
            if self.closed:
                return

            self.get_current_status = lambda: "Binding books... %.0f%%" % (
                self.app.progress
            )
            self.send_sync("Binding books...")
            self.app.bind_books()
            self.get_current_status = None
            if self.closed:
                return

            self.send_sync("Compressing output folder...")
            self.app.compress_books()
            if self.closed:
                return

            assert isinstance(self.app.archived_outputs, list)
            for archive in self.app.archived_outputs:
                self.upload_file(archive)

        except Exception as ex:
            logger.exception("Failed to download")
            self.send_sync("Download failed!\n`%s`" % str(ex))
        finally:
            self.destroy()

    def upload_file(self, archive):
        # Check file size
        filename = os.path.basename(archive)
        file_size = os.stat(archive).st_size
        if file_size > 24.99 * 1024 * 1024:
            self.send_sync("File exceeds 25MB. Using alternative cloud storage.")
            try:
                description = "Generated By : Lightnovel Crawler Discord Bot"
                direct_link = upload(archive, description)
                self.send_sync(direct_link)
            except Exception as e:
                logger.error("Failed to upload file: %s", archive, e)
                self.send_sync(f"Failed to upload file: {filename}.\n`Error: {e}`")

            return

        # Upload small files to discord directly
        k = 0
        while file_size > 1024 and k < 3:
            k += 1
            file_size /= 1024.0

        self.send_sync(
            "Uploading %s [%d%s] ..."
            % (
                os.path.basename(archive),
                int(file_size * 100) / 100.0,
                ["B", "KB", "MB", "GB"][k],
            )
        )
        self.wait_for(
            self.user.send(
                file=discord.File(open(archive, "rb"), os.path.basename(archive))
            )
        )
