import logging
import os
import re
import shutil
from urllib.parse import urlparse

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          ConversationHandler, Job, MessageHandler, filters)

from lncrawl.core.app import App
from lncrawl.core.sources import prepare_crawler
from lncrawl.utils.uploader import upload

logger = logging.getLogger(__name__)


available_formats = [
    "epub",
    "text",
    "web",
    "mobi",
    "pdf",
]


class TelegramBot:
    def start(self):
        os.environ["debug_mode"] = "yes"

        # Build the Application and with bot's token.
        TOKEN = os.getenv("TELEGRAM_TOKEN", "")
        self.application = Application.builder().token(TOKEN).build()

        # Add a command helper for help
        self.application.add_handler(CommandHandler("help", self.show_help))

        # Add conversation handler with states
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", self.init_app),
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), self.handle_novel_url
                ),
            ],
            fallbacks=[
                CommandHandler("cancel", self.destroy_app),
            ],
            states={
                "handle_novel_url": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_novel_url
                    ),
                ],
                "handle_crawler_to_search": [
                    CommandHandler(
                        "skip", self.handle_crawler_to_search
                    ),
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
                    CommandHandler(
                        "first", self.handle_range_first
                    ),
                    CommandHandler(
                        "volume", self.handle_range_volume
                    ),
                    CommandHandler(
                        "chapter", self.handle_range_chapter
                    ),
                    MessageHandler(filters.TEXT & ~(filters.COMMAND), self.display_range_selection_help),
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
            MessageHandler(filters.TEXT, self.handle_downloader)
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
        """Log Errors caused by Updates."""
        logger.warning("Error: %s\nCaused by: %s", context.error, update)

    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Send /start to create new session.\n")
        return ConversationHandler.END

    def get_current_jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id=None):
        if update:
            name = str(update.effective_message.chat_id)
        else:
            name = chat_id
        current_jobs = context.job_queue.get_jobs_by_name(name)
        return current_jobs

    async def destroy_app(self, update: Update, context: ContextTypes.DEFAULT_TYPE, job: Job = None):
        if update:
            chat_id = str(update.effective_message.chat_id)
        else:
            chat_id = job.chat_id

        for job in self.get_current_jobs(update, context, chat_id):
            job.schedule_removal()

        if job or context.user_data.get("app"):
            app = job.data.pop("app", None) or context.user_data.pop("app")
            app.destroy()
            # remove output path
            # shutil.rmtree(app.output_path, ignore_errors=True)

        await context.bot.send_message(chat_id, text="Session closed", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    async def init_app(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get("app"):
            await self.destroy_app(update, context)

        app = App()
        app.initialize()
        context.user_data["app"] = app
        await update.message.reply_text("A new session is created.")

        await update.message.reply_text(
            "I recognize input of these two categories:\n"
            "- Profile page url of a lightnovel.\n"
            "- A query to search your lightnovel.\n"
            "Enter whatever you want or send /cancel to stop."
        )
        return "handle_novel_url"

    async def handle_novel_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.get_current_jobs(update, context):
            app = context.user_data.get("app")
            await update.message.reply_text(
                "%s\n"
                "%d out of %d chapters has been downloaded.\n"
                "To terminate this session send /cancel."
                % (context.user_data.get("status"), app.progress, len(app.chapters))
            )
        else:
            if context.user_data.get("app"):
                app = context.user_data.get("app")
            else:
                app = App()
                app.initialize()
                context.user_data["app"] = app

            app.user_input = update.message.text.strip()

            try:
                app.prepare_search()
            except Exception:
                await update.message.reply_text(
                    "Sorry! I only recognize these sources:\n"
                    + "https://github.com/dipu-bd/lightnovel-crawler#supported-sources"
                )
                await update.message.reply_text(
                    "Enter something again or send /cancel to stop."
                )
                await update.message.reply_text(
                    "You can send the novelupdates link of the novel too.",
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

    async def show_crawlers_to_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

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

    async def handle_crawler_to_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

        link = update.message.text
        if link:
            selected_crawlers = []
            if link.isdigit():
                selected_crawlers += [app.crawler_links[int(link) - 1]]
            else:
                selected_crawlers += [
                    x
                    for i, x in enumerate(app.crawler_links)
                    if "%d - %s" % (i + 1, urlparse(x).hostname) == link
                ]

            if len(selected_crawlers) != 0:
                app.crawler_links = selected_crawlers

        await update.message.reply_text(
            'Searching for "%s" in %d sites. Please wait.'
            % (app.user_input, len(app.crawler_links)),
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            "DO NOT type anything until I reply.\n"
            "You can only send /cancel to stop this session."
        )

        app.search_novel()
        return await self.show_novel_selection(update, context)

    async def show_novel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

        if len(app.search_results) == 0:
            await update.message.reply_text(
                "No results found by your query.\n" "Try again or send /cancel to stop."
            )
            return "handle_novel_url"

        if len(app.search_results) == 1:
            context.user_data["selected"] = app.search_results[0]
            return self.show_source_selection(update, context)

        await update.message.reply_text(
            "Choose any one of the following novels,"
            + " or send /cancel to stop this session.",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        "%d. %s (in %d sources)"
                        % (index + 1, res["title"], len(res["novels"]))
                    ]
                    for index, res in enumerate(app.search_results)
                ],
                one_time_keyboard=True,
            ),
        )

        return "handle_select_novel"

    async def handle_select_novel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

        selected = None
        text = update.message.text
        if text:
            if text.isdigit():
                selected = app.search_results[int(text) - 1]
            else:
                for i, item in enumerate(app.search_results[:10]):
                    sample = "%d. %s" % (i + 1, item["title"])
                    if text.startswith(sample):
                        selected = item
                    elif len(text) >= 5 and text.lower() in item["title"].lower():
                        selected = item
                    else:
                        continue

                    break

        if not selected:
            return await self.show_novel_selection(update, context)

        context.user_data["selected"] = selected
        return await self.show_source_selection(update, context)

    async def show_source_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        selected = context.user_data.get("selected")
        assert isinstance(app, App)

        if len(selected["novels"]) == 1:
            app.crawler = prepare_crawler(selected["novels"][0]["url"])
            return await self.get_novel_info(update, context)

        await update.message.reply_text(
            ('Choose a source to download "%s", ' % selected["title"])
            + "or send /cancel to stop this session.",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        "%d. %s %s"
                        % (
                            index + 1,
                            novel["url"],
                            novel["info"] if "info" in novel else "",
                        )
                    ]
                    for index, novel in enumerate(selected["novels"])
                ],
                one_time_keyboard=True,
            ),
        )

        return "handle_select_source"

    async def handle_select_source(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        selected = context.user_data.get("selected")
        assert isinstance(app, App)

        source = None
        text = update.message.text
        if text:
            if text.isdigit():
                source = selected["novels"][int(text) - 1]
            else:
                for i, item in enumerate(selected["novels"]):
                    sample = "%d. %s" % (i + 1, item["url"])
                    if text.startswith(sample):
                        source = item
                    elif len(text) >= 5 and text.lower() in item["url"].lower():
                        source = item
                    else:
                        continue

                    break

        if not selected or not (source and source.get("url")):
            return await self.show_source_selection(update, context)

        app.crawler = prepare_crawler(source.get("url"))
        return await self.get_novel_info(update, context)

    async def get_novel_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        # user = update.message.from_user

        await update.message.reply_text(app.crawler.novel_url)

        # TODO: Implement login feature. Create login_info_dict of (email, password)
        # if app.can_do('login'):
        #     app.login_data = login_info_dict.get(app.crawler.home_url)
        #

        await update.message.reply_text("Reading novel info...")
        app.get_novel_info()

        if os.path.exists(app.output_path):
            await update.message.reply_text(
                "Local cache found do you want to use it",
                reply_markup=ReplyKeyboardMarkup(
                    [["Yes", "No"]], one_time_keyboard=True
                ),
            )
            return "handle_delete_cache"
        else:
            os.makedirs(app.output_path, exist_ok=True)
            # Get chapter range
            await update.message.reply_text(
                "%d volumes and %d chapters found."
                % (len(app.crawler.volumes), len(app.crawler.chapters)),
                reply_markup=ReplyKeyboardRemove(),
            )
            return await self.display_range_selection_help(update)

    async def handle_delete_cache(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        text = update.message.text
        if text.startswith("No"):
            if os.path.exists(app.output_path):
                shutil.rmtree(app.output_path, ignore_errors=True)
            os.makedirs(app.output_path, exist_ok=True)

        # Get chapter range
        await update.message.reply_text(
            "%d volumes and %d chapters found."
            % (len(app.crawler.volumes), len(app.crawler.chapters)),
            reply_markup=ReplyKeyboardRemove(),
        )
        return await self.display_range_selection_help(update)

    async def display_range_selection_help(self, update):
        await update.message.reply_text(
            "\n".join(
                [
                    "Send /all to download everything.",
                    "Send /last to download last 50 chapters.",
                    "Send /first to download first 50 chapters.",
                    "Send /volume to choose specific volumes to download",
                    "Send /chapter to choose a chapter range to download",
                    "To tereminate this session, send /cancel.",
                ]
            )
        )
        return "handle_range_selection"

    async def range_selection_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        await update.message.reply_text(
            "You have selected %d chapters to download" % len(app.chapters)
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

    async def handle_range_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        app.chapters = app.crawler.chapters[:]
        return await self.range_selection_done(update, context)

    async def handle_range_first(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        app.chapters = app.crawler.chapters[:50]
        return await self.range_selection_done(update, context)

    async def handle_range_last(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        app.chapters = app.crawler.chapters[-50:]
        return await self.range_selection_done(update, context)

    async def handle_range_volume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        buttons = [str(vol["id"]) for vol in app.crawler.volumes]
        await update.message.reply_text(
            "I got these volumes: "
            + ", ".join(buttons)
            + "\nEnter which one these volumes you want to download separated space or commas."
        )
        return "handle_volume_selection"

    async def handle_volume_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

        text = update.message.text
        selected = re.findall(r"\d+", text)
        await update.message.reply_text(
            "Got the volumes: " + ", ".join(selected),
        )

        selected = [int(x) for x in selected]
        app.chapters = [
            chap for chap in app.crawler.chapters if selected.count(chap["volume"]) > 0
        ]
        return await self.range_selection_done(update, context)

    async def handle_range_chapter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        chapters = app.crawler.chapters
        await update.message.reply_text(
            "I got %s  chapters" % len(chapters)
            + "\nEnter which start and end chapter you want to generate separated space or comma.",
        )
        return "handle_chapter_selection"

    async def handle_chapter_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        text = update.message.text
        selected = re.findall(r"\d+", text)
        # print(selected)
        if len(selected) != 2:
            await update.message.reply_text("Sorry, I did not understand. Please try again")
            return "handle_range_chapter"
        else:
            selected = [int(x) for x in selected]
            app.chapters = app.crawler.chapters[selected[0] - 1 : selected[1]]
            await update.message.reply_text(
                "Got the start chapter : %s" % selected[0]
                + "\nThe end chapter : %s" % selected[1]
                + "\nTotal chapter chosen is %s" % len(app.chapters),
            )
        return await self.range_selection_done(update, context)

    async def handle_pack_by_volume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

        text = update.message.text
        app.pack_by_volume = text.startswith("Split")

        if app.pack_by_volume:
            await update.message.reply_text("I will split output files into volumes")
        else:
            await update.message.reply_text(
                "I will generate single output files whenever possible"
            )

        i = 0
        new_list = [["all"]]
        while i < len(available_formats):
            new_list.append(available_formats[i : i + 2])
            i += 2

        await update.message.reply_text(
            "In which format you want me to generate your book?",
            reply_markup=ReplyKeyboardMarkup(
                new_list,
                one_time_keyboard=True,
            ),
        )

        return "handle_output_format"

    async def handle_output_format(self, update, context):
        app = context.user_data.get("app")
        user = update.message.from_user

        text = update.message.text.strip().lower()
        app.output_formats = {}
        if text in available_formats:
            for x in available_formats:
                if x == text:
                    app.output_formats[x] = True
                else:
                    app.output_formats[x] = False

        elif text != "all":
            await update.message.reply_text("Sorry, I did not understand.")
            return

        chat_id = update.effective_message.chat_id
        job = context.job_queue.run_once(
            self.process_download_request,
            1,
            name=str(user.id),
            chat_id=chat_id,
            data=context.user_data
        )
        context.user_data["job"] = job

        await update.message.reply_text(
            "Your request has been received."
            'I will generate book in "%s" format' % text,
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    async def process_download_request(self, context):
        job = context.job
        user_data = job.data
        app = user_data.get("app")
        if app:
            user_data["status"] = 'Downloading "%s"' % app.crawler.novel_title
            app.start_download()
            await context.bot.send_message(job.chat_id, text="Download finished.")

        app = user_data.get("app")
        if app:
            user_data["status"] = "Generating output files"
            await context.bot.send_message(job.chat_id, text=user_data.get("status"))
            output_files = app.bind_books()
            logger.debug("Output files: %s", output_files)
            await context.bot.send_message(job.chat_id, text="Output files generated.")

        app = user_data.get("app")
        if app:
            user_data["status"] = "Compressing output folder."
            await context.bot.send_message(job.chat_id, text=user_data.get("status"))
            app.compress_books()

        for archive in app.archived_outputs:
            file_size = os.stat(archive).st_size
            if file_size < 49.99 * 1024 * 1024:
                await context.bot.send_document(
                    job.chat_id,
                    open(archive, "rb")
                )
            else:
                await context.bot.send_message(job.chat_id, text="File size more than 50 MB so cannot be sent via telegram bot.\n"
                                               + "Uploading to alternative cloud storage"
                                               )
                try:
                    description = "Generated By : Lightnovel Crawler Telegram Bot"
                    direct_link = upload(archive, description)
                    await context.bot.send_message(job.chat_id, text="Get your file here: %s" % direct_link)
                except Exception as e:
                    logger.error("Failed to upload file: %s", archive, e)

        await self.destroy_app(None, context, job)

    async def handle_downloader(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        job = self.get_current_jobs(update, context)

        if app or job:
            await update.message.reply_text(
                "%s\n"
                "%d out of %d chapters has been downloaded.\n"
                "To terminate this session send /cancel."
                % (context.user_data.get("status"), app.progress, len(app.chapters))
            )
        # else:
        #     self.show_help(bot, update)

        return ConversationHandler.END
