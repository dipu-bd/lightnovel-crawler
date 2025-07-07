import asyncio
import logging
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from urllib.parse import urlparse

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from lncrawl.core.app import App
from lncrawl.core.sources import prepare_crawler
from lncrawl.utils.uploader import upload

logger = logging.getLogger(__name__)

available_formats = ["epub", "text", "web", "mobi", "pdf"]


class TelegramBot:
    def __init__(self):
        self.executor = ThreadPoolExecutor(
            max_workers=10, thread_name_prefix="telegram_bot"
        )
        self.active_sessions: Dict[str, dict] = {}  # Track active user sessions
        self.max_active_sessions = 50  # Maximum concurrent sessions

    def start(self):
        os.environ["debug_mode"] = "yes"

        # Build the Application and with bot's token.
        TOKEN = os.getenv("TELEGRAM_TOKEN", "")
        if not TOKEN:
            raise Exception("Telegram token not found")

        self.application = Application.builder().token(TOKEN).build()
        self.application.add_handler(CommandHandler("help", self.show_help))
        self.application.add_handler(CommandHandler("status", self.handle_downloader))
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", self.init_app),
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), self.handle_novel_url
                ),
            ],
            fallbacks=[CommandHandler("cancel", self.destroy_app)],
            states={
                "handle_novel_url": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_novel_url
                    ),
                ],
                "handle_crawler_to_search": [
                    CommandHandler("skip", self.handle_crawler_to_search),
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_crawler_to_search
                    ),
                ],
                "handle_select_novel": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_select_novel
                    ),
                ],
                "handle_select_source": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_select_source
                    ),
                ],
                "handle_delete_cache": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_delete_cache
                    ),
                ],
                "handle_range_selection": [
                    CommandHandler("all", self.handle_range_all),
                    CommandHandler("last", self.handle_range_last),
                    CommandHandler("first", self.handle_range_first),
                    CommandHandler("volume", self.handle_range_volume),
                    CommandHandler("chapter", self.handle_range_chapter),
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND),
                        self.display_range_selection_help,
                    ),
                ],
                "handle_volume_selection": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_volume_selection
                    ),
                ],
                "handle_chapter_selection": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_chapter_selection
                    ),
                ],
                "handle_pack_by_volume": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_pack_by_volume
                    ),
                ],
                "handle_output_format": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_output_format
                    ),
                ],
            },
        )
        self.application.add_handler(conv_handler)

        # Fallback helper
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_downloader)
        )

        # Log all errors
        self.application.add_error_handler(self.error_handler)
        print("Telegram bot is online!")

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # Start the Bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.warning("Error: %s\nCaused by: %s", context.error, update)

    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Send /start to create a new session.\n"
            "Send /status to check the status of your current download.\n"
            "Send /cancel to stop your current session."
        )
        return ConversationHandler.END

    def get_current_jobs(self, chat_id: str, context: ContextTypes.DEFAULT_TYPE):
        return context.job_queue.get_jobs_by_name(
            chat_id
        ) + context.job_queue.get_jobs_by_name(f"{chat_id}_progress")

    async def destroy_app(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, job=None
    ):
        chat_id = str(update.effective_message.chat_id) if update else job.chat_id
        session = self.active_sessions.get(chat_id)

        if session:
            for future_key in ["download_future", "bind_future"]:
                future = session.get(future_key)
                if future and not future.done():
                    future.cancel()
                    logger.info("Cancelled %s for chat_id %s", future_key, chat_id)

        for job in self.get_current_jobs(chat_id, context):
            job.schedule_removal()

        if session:
            app = session.get("app")
            if app:
                try:
                    app.destroy()
                except Exception as e:
                    logger.exception(
                        "Failed to destroy app for chat_id %s: % komunikat: %s",
                        chat_id,
                        e,
                    )
                finally:
                    self.active_sessions.pop(chat_id, None)
                    logger.info("Session destroyed for chat_id: %s", chat_id)

        await context.bot.send_message(
            chat_id, text="Session closed", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def init_app(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_message.chat_id)

        # Check if user already has an active session
        if chat_id in self.active_sessions:
            await update.message.reply_text(
                "You already have an active session. Please send /cancel to close it before starting a new one."
            )
            return ConversationHandler.END

        # Check session limit
        if len(self.active_sessions) >= self.max_active_sessions:
            await update.message.reply_text(
                "Sorry, the bot is currently handling too many requests. Please try again later."
            )
            return ConversationHandler.END

        app = App()
        root = os.path.abspath(".telegram_bot_output")
        good_name = os.path.basename(app.output_path)
        output_path = os.path.join(root, chat_id, good_name)
        app.output_path = output_path

        self.active_sessions[chat_id] = {
            "app": app,
            "status": "Initialized",
            "error": None,
        }
        await update.message.reply_text("A new session is created.")
        await update.message.reply_text(
            "I recognize input of these two categories:\n"
            "- Profile page url of a lightnovel.\n"
            "- A query to search your lightnovel.\n"
            "Enter whatever you want or send /cancel to stop."
        )
        return "handle_novel_url"

    async def handle_novel_url(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)

        if not session:
            await update.message.reply_text("Please start a new session with /start.")
            return ConversationHandler.END

        if self.get_current_jobs(chat_id, context):
            app = session.get("app")
            status = session.get("status", "Processing...")
            await update.message.reply_text(
                f"{status}\n"
                f"{int(app.progress)} out of {len(app.chapters)} chapters has been downloaded.\n"
                f"To terminate this session send /cancel."
            )
            return "handle_novel_url"

        app = session.get("app", App())
        self.active_sessions[chat_id]["app"] = app
        app.user_input = update.message.text.strip()

        try:
            app.prepare_search()
        except Exception as e:
            logger.exception("Failed to init crawler for chat_id %s: %s", chat_id, e)
            await update.message.reply_text(
                "Sorry! I only recognize these sources:\n"
                "https://github.com/dipu-bd/lightnovel-crawler#supported-sources\n"
                "Enter something again or send /cancel to stop.\n"
                "You can send the novelupdates link of the novel too."
            )
            return "handle_novel_url"

        if app.crawler:
            await update.message.reply_text("Got your page link")
            return await self.get_novel_info(update, context)

        if len(app.user_input) < 5:
            await update.message.reply_text(
                "Please enter a longer query text (at least 5 letters)."
            )
            return "handle_novel_url"

        await update.message.reply_text("Got your query text")
        return await self.show_crawlers_to_search(update, context)

    async def show_crawlers_to_search(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")

        buttons = []

        def make_button(i, url):
            return "%d - %s" % (i + 1, urlparse(url).hostname)

        for i in range(1, len(app.crawler_links) + 1, 2):
            buttons += [
                [
                    make_button(i - 1, app.crawler_links[i - 1]),
                    make_button(i, app.crawler_links[i])
                    if i < len(app.crawler_links)
                    else "",
                ]
            ]

        await update.message.reply_text(
            "Choose where to search for your novel, \n"
            "or send /skip to search everywhere.",
            reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True),
        )
        return "handle_crawler_to_search"

    async def handle_crawler_to_search(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        link = update.message.text.strip()
        if link and link != "/skip":
            selected_crawlers = []
            if link.isdigit():
                idx = int(link) - 1
                if 0 <= idx < len(app.crawler_links):
                    selected_crawlers.append(app.crawler_links[idx])
            else:
                selected_crawlers = [
                    x
                    for i, x in enumerate(app.crawler_links)
                    if f"{i + 1} - {urlparse(x).hostname}" == link
                ]
            if selected_crawlers:
                app.crawler_links = selected_crawlers

        await update.message.reply_text(
            f'Searching for "{app.user_input}" in {len(app.crawler_links)} sites. Please wait.',
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            "DO NOT type anything until I reply.\n"
            "You can only send /cancel to stop this session."
        )

        # Run search in a separate thread
        future = self.executor.submit(app.search_novel)
        while not future.done():
            await asyncio.sleep(1)
        if future.exception():
            logger.exception(
                "Search failed for chat_id %s: %s", chat_id, future.exception()
            )
            await update.message.reply_text(f"Search failed: {future.exception()}")
            return await self.destroy_app(update, context)

        return await self.show_novel_selection(update, context)

    async def show_novel_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        if len(app.search_results) == 0:
            await update.message.reply_text(
                "No results found by your query.\nTry again or send /cancel to stop."
            )
            return "handle_novel_url"

        if len(app.search_results) == 1:
            session["selected"] = app.search_results[0]
            return await self.show_source_selection(update, context)

        buttons = [
            [f"{i + 1}. {res['title']} (in {len(res['novels'])} sources)"]
            for i, res in enumerate(app.search_results)
        ]
        await update.message.reply_text(
            "Choose any one of the following novels, or send /cancel to stop this session.",
            reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True),
        )
        return "handle_select_novel"

    async def handle_select_novel(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        text = update.message.text.strip()
        selected = None
        if text.isdigit():
            idx = int(text) - 1
            if 0 <= idx < len(app.search_results):
                selected = app.search_results[idx]
        else:
            for i, item in enumerate(app.search_results):
                sample = f"{i + 1}. {item['title']}"
                if text.startswith(sample) or (
                    len(text) >= 5 and text.lower() in item["title"].lower()
                ):
                    selected = item
                    break

        if not selected:
            await update.message.reply_text(
                "Please select a valid novel from the list."
            )
            return await self.show_novel_selection(update, context)

        session["selected"] = selected
        return await self.show_source_selection(update, context)

    async def show_source_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        selected = session.get("selected")
        if len(selected["novels"]) == 1:
            app = session.get("app")
            app.crawler = prepare_crawler(selected["novels"][0]["url"])
            return await self.get_novel_info(update, context)

        buttons = [
            [f"{i + 1}. {novel['url']} {novel.get('info', '')}"]
            for i, novel in enumerate(selected["novels"])
        ]
        await update.message.reply_text(
            f'Choose a source to download "{selected["title"]}", or send /cancel to stop this session.',
            reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True),
        )
        return "handle_select_source"

    async def handle_select_source(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        selected = session.get("selected")
        text = update.message.text.strip()
        source = None
        if text.isdigit():
            idx = int(text) - 1
            if 0 <= idx < len(selected["novels"]):
                source = selected["novels"][idx]
        else:
            for i, item in enumerate(selected["novels"]):
                sample = f"{i + 1}. {item['url']}"
                if text.startswith(sample) or (
                    len(text) >= 5 and text.lower() in item["url"].lower()
                ):
                    source = item
                    break

        if not source:
            await update.message.reply_text(
                "Please select a valid source from the list."
            )
            return await self.show_source_selection(update, context)

        app = session.get("app")
        app.crawler = prepare_crawler(source["url"])
        return await self.get_novel_info(update, context)

    async def get_novel_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        await update.message.reply_text(f"Novel URL: {app.crawler.novel_url}")
        await update.message.reply_text("Reading novel info...")

        # Run get_novel_info in a separate thread
        future = self.executor.submit(app.get_novel_info)
        while not future.done():
            await asyncio.sleep(1)
        if future.exception():
            logger.exception(
                "Failed to get novel info for chat_id %s: %s",
                chat_id,
                future.exception(),
            )
            await update.message.reply_text(
                f"Failed to get novel info: {future.exception()}"
            )
            return await self.destroy_app(update, context)

        if os.path.exists(f"{app.output_path}/json"):
            await update.message.reply_text(
                "Local cache found. Do you want to use it?",
                reply_markup=ReplyKeyboardMarkup(
                    [["Yes", "No"]], one_time_keyboard=True
                ),
            )
            return "handle_delete_cache"
        else:
            os.makedirs(app.output_path, exist_ok=True)
            await update.message.reply_text(
                f"{len(app.crawler.volumes)} volumes and {len(app.crawler.chapters)} chapters found.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return await self.display_range_selection_help(update)

    async def handle_delete_cache(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        if update.message.text.startswith("No"):
            shutil.rmtree(app.output_path, ignore_errors=True)
            os.makedirs(app.output_path, exist_ok=True)

        await update.message.reply_text(
            f"{len(app.crawler.volumes)} volumes and {len(app.crawler.chapters)} chapters found.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return await self.display_range_selection_help(update)

    async def display_range_selection_help(self, update: Update):
        await update.message.reply_text(
            "\n".join(
                [
                    "Send /all to download everything.",
                    "Send /last to download last 50 chapters.",
                    "Send /first to download first 50 chapters.",
                    "Send /volume to choose specific volumes to download",
                    "Send /chapter to choose a chapter range to download",
                    "To terminate this session, send /cancel.",
                ]
            )
        )
        return "handle_range_selection"

    async def range_selection_done(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        await update.message.reply_text(
            f"You have selected {len(app.chapters)} chapters to download"
        )
        if len(app.chapters) == 0:
            return await self.display_range_selection_help(update)

        await update.message.reply_text(
            "Do you want to generate a single file or split the books into volumes?",
            reply_markup=ReplyKeyboardMarkup(
                [["Single file", "Split by volumes"]], one_time_keyboard=True
            ),
        )
        return "handle_pack_by_volume"

    async def handle_range_all(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        app.chapters = app.crawler.chapters[:]
        return await self.range_selection_done(update, context)

    async def handle_range_first(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        app.chapters = app.crawler.chapters[:50]
        return await self.range_selection_done(update, context)

    async def handle_range_last(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        app.chapters = app.crawler.chapters[-50:]
        return await self.range_selection_done(update, context)

    async def handle_range_volume(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        buttons = [str(vol["id"]) for vol in app.crawler.volumes]
        await update.message.reply_text(
            f"I got these volumes: {', '.join(buttons)}\n"
            "Enter which one these volumes you want to download separated by space or commas."
        )
        return "handle_volume_selection"

    async def handle_volume_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        text = update.message.text
        selected = re.findall(r"\d+", text)
        await update.message.reply_text(f"Got the volumes: {', '.join(selected)}")
        selected = [int(x) for x in selected]
        app.chapters = [
            chap for chap in app.crawler.chapters if chap["volume"] in selected
        ]
        return await self.range_selection_done(update, context)

    async def handle_range_chapter(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        await update.message.reply_text(
            f"I got {len(app.crawler.chapters)} chapters\n"
            "Enter which start and end chapter you want to generate separated by space or comma."
        )
        return "handle_chapter_selection"

    async def handle_chapter_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        text = update.message.text
        selected = re.findall(r"\d+", text)
        if len(selected) != 2:
            await update.message.reply_text(
                "Sorry, I did not understand. Please try again"
            )
            return "handle_range_chapter"
        selected = [int(x) for x in selected]
        if (
            selected[0] < 1
            or selected[1] > len(app.crawler.chapters)
            or selected[0] > selected[1]
        ):
            await update.message.reply_text("Invalid chapter range. Please try again")
            return "handle_range_chapter"
        app.chapters = app.crawler.chapters[selected[0] - 1 : selected[1]]
        await update.message.reply_text(
            f"Got the start chapter: {selected[0]}\n"
            f"The end chapter: {selected[1]}\n"
            f"Total chapters chosen: {len(app.chapters)}"
        )
        return await self.range_selection_done(update, context)

    async def handle_pack_by_volume(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        app.pack_by_volume = update.message.text.startswith("Split")
        await update.message.reply_text(
            "I will split output files into volumes"
            if app.pack_by_volume
            else "I will generate single output files whenever possible"
        )

        new_list = [["all"]] + [
            available_formats[i : i + 2] for i in range(0, len(available_formats), 2)
        ]
        await update.message.reply_text(
            "In which format do you want me to generate your book?",
            reply_markup=ReplyKeyboardMarkup(new_list, one_time_keyboard=True),
        )
        return "handle_output_format"

    async def handle_output_format(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        app = session.get("app")
        text = update.message.text.strip().lower()
        if text == "all":
            app.output_formats = {x: True for x in available_formats}
        elif text in available_formats:
            app.output_formats = {x: x == text for x in available_formats}
        else:
            await update.message.reply_text(
                f"Sorry, I did not understand. Try one of: {' '.join(available_formats)} or 'all'"
            )
            return "handle_output_format"

        # Schedule the download process as a job
        job = context.job_queue.run_once(
            self.start_download_process,
            1,
            name=chat_id,
            chat_id=chat_id,
            data={"app": app, "chat_id": chat_id},
        )
        session["job"] = job
        session["status"] = "Starting download..."
        await update.message.reply_text(
            f"Your request has been received. I will generate book in {', '.join(k for k, v in app.output_formats.items() if v)} format(s)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    async def start_download_process(self, context):
        job = context.job
        chat_id = job.data["chat_id"]
        session = self.active_sessions.get(chat_id)
        if not session:
            await context.bot.send_message(chat_id, text="Error: Session not found.")
            return

        app = session.get("app")
        if not app:
            await context.bot.send_message(
                chat_id, text="Error: No app instance found."
            )
            return await self.destroy_app(None, context, job)

        # Start the download process in a separate thread
        session["download_future"] = self.executor.submit(
            self.run_download, app, chat_id, session, context
        )
        # Schedule a polling job to check progress
        context.job_queue.run_repeating(
            self.check_download_progress,
            interval=5,
            name=f"{chat_id}_progress",
            chat_id=chat_id,
            data={"app": app, "chat_id": chat_id},
        )

    def run_download(self, app, chat_id, session, context):
        try:
            session["status"] = f'Downloading "{app.crawler.novel_title}"'
            for _ in app.start_download():
                pass
            session["status"] = "Download finished"
            session["download_future"] = None
            session["bind_future"] = self.executor.submit(
                self.run_bind_books, app, chat_id, session, context
            )
        except Exception as e:
            logger.exception("Failed to download for chat_id %s: %s", chat_id, e)
            session["error"] = f"Download failed: {e}"

    def run_bind_books(self, app, chat_id, session, context):
        try:
            session["status"] = "Generating output files"
            for _ in app.bind_books():
                pass
            session["status"] = "Output files generated"
            session["bind_future"] = None
            session["upload_pending"] = True
        except Exception as e:
            logger.exception("Failed to bind books for chat_id %s: %s", chat_id, e)
            session["error"] = f"Binding books failed: {e}"

    async def check_download_progress(self, context):
        job = context.job
        chat_id = job.data["chat_id"]
        session = self.active_sessions.get(chat_id)
        if not session:
            job.schedule_removal()
            return

        app = session.get("app")
        if session.get("error"):
            await context.bot.send_message(chat_id, text=session["error"])
            job.schedule_removal()
            return await self.destroy_app(None, context, job)

        if session.get("status") in ["Download finished", "Output files generated"]:
            await context.bot.send_message(
                chat_id,
                text=session["status"],
            )

        if session.get("upload_pending"):
            if not hasattr(app, "archived_outputs") or not app.archived_outputs:
                await context.bot.send_message(
                    chat_id, text="No output files were generated."
                )
                job.schedule_removal()
                return await self.destroy_app(None, context, job)

            for archive in app.archived_outputs:
                file_size = os.stat(archive).st_size
                if file_size < 49.99 * 1024 * 1024:
                    await context.bot.send_document(
                        chat_id,
                        document=open(archive, "rb"),
                        filename=os.path.basename(archive),
                    )
                else:
                    await context.bot.send_message(
                        chat_id,
                        text="File size exceeds 50 MB, uploading to alternative cloud storage.",
                    )
                    try:
                        description = "Generated By: Lightnovel Crawler Telegram Bot"
                        direct_link = upload(archive, description)
                        await context.bot.send_message(
                            chat_id, text=f"Get your file here: {direct_link}"
                        )
                    except Exception as e:
                        logger.error(
                            "Failed to upload file %s for chat_id %s: %s",
                            archive,
                            chat_id,
                            e,
                        )
                        await context.bot.send_message(
                            chat_id,
                            text=f"Failed to upload file {os.path.basename(archive)}: {e}",
                        )

            session["upload_pending"] = False
            job.schedule_removal()
            await self.destroy_app(None, context, job)

    async def handle_downloader(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = str(update.effective_message.chat_id)
        session = self.active_sessions.get(chat_id)
        if session:
            app = session.get("app")
            status = session.get("status", "Processing...")
            if app and hasattr(app, "chapters") and len(app.chapters) > 0:
                await update.message.reply_text(
                    f"{status}\n"
                    f"{int(app.progress)}% out of {len(app.chapters)} chapters has been downloaded.\n"
                    # "To terminate this session send /cancel."
                )
            else:
                await update.message.reply_text(
                    f"{status}\n"
                    "No chapters selected yet. Please continue with your selection or send /cancel."
                )
        else:
            await update.message.reply_text(
                "No active session. Please start a new session with /start."
            )
        return ConversationHandler.END
