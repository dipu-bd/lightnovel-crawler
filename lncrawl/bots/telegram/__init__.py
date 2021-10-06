# -*- coding: utf-8 -*-
import logging
import os
import re
import shutil
from urllib.parse import urlparse

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from lncrawl.core.app import App
from lncrawl.utils.uploader import upload

logger = logging.getLogger(__name__)


available_formats = [
    'epub',
    'text',
    'web',
    'mobi',
    'pdf',
]


class TelegramBot:
    def start(self):
        os.environ['debug_mode'] = 'yes'

        # Create the EventHandler and pass it your bot's token.
        self.updater = Updater(
            os.getenv('TELEGRAM_TOKEN', ''),
            # persistence=PicklePersistence('lncrawl.botdata') # No persistency under v12.0
        )

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # Add a command helper for help
        dp.add_handler(CommandHandler('help', self.show_help))

        # Add conversation handler with states
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.init_app, pass_user_data=True),
                MessageHandler(
                    Filters.text, self.handle_novel_url, pass_user_data=True),
            ],
            fallbacks=[
                CommandHandler('cancel', self.destroy_app,
                               pass_user_data=True),
            ],
            states={
                'handle_novel_url': [
                    MessageHandler(
                        Filters.text, self.handle_novel_url, pass_user_data=True),
                ],
                'handle_crawler_to_search': [
                    CommandHandler(
                        'skip', self.handle_crawler_to_search, pass_user_data=True),
                    MessageHandler(
                        Filters.text, self.handle_crawler_to_search, pass_user_data=True),
                ],
                'handle_select_novel': [
                    MessageHandler(
                        Filters.text, self.handle_select_novel, pass_user_data=True),
                ],
                'handle_select_source': [
                    MessageHandler(
                        Filters.text, self.handle_select_source, pass_user_data=True),
                ],
                'handle_delete_cache': [
                    MessageHandler(
                        Filters.text, self.handle_delete_cache, pass_user_data=True),
                ],
                'handle_range_selection': [
                    CommandHandler('all', self.handle_range_all,
                                   pass_user_data=True),
                    CommandHandler('last', self.handle_range_last,
                                   pass_user_data=True),
                    CommandHandler(
                        'first', self.handle_range_first, pass_user_data=True),
                    CommandHandler(
                        'volume', self.handle_range_volume, pass_user_data=True),
                    CommandHandler(
                        'chapter', self.handle_range_chapter, pass_user_data=True),
                    MessageHandler(
                        Filters.text, self.display_range_selection_help),
                ],
                'handle_volume_selection': [
                    MessageHandler(
                        Filters.text, self.handle_volume_selection, pass_user_data=True),
                ],
                'handle_chapter_selection': [
                    MessageHandler(
                        Filters.text, self.handle_chapter_selection, pass_user_data=True),
                ],
                'handle_pack_by_volume': [
                    MessageHandler(
                        Filters.text, self.handle_pack_by_volume, pass_user_data=True),
                ],
                'handle_output_format': [
                    MessageHandler(
                        Filters.text, self.handle_output_format, pass_job_queue=True, pass_user_data=True),
                ],
            },
        )
        dp.add_handler(conv_handler)

        # Fallback helper
        dp.add_handler(MessageHandler(
            Filters.text, self.handle_downloader, pass_user_data=True))

        # Log all errors
        dp.add_error_handler(self.error_handler)

        # Start the Bot
        self.updater.start_polling()

        print('Telegram bot is online!')

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
    # end def

    def error_handler(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warn('Error: %s\nCaused by: %s', error, update)
    # end def

    def show_help(self, bot, update):
        update.message.reply_text(
            'Send /start to create new session.\n'
        )
        return ConversationHandler.END
    # end def

    def destroy_app(self, bot, update, user_data):
        if user_data.get('job'):
            user_data.pop('job').schedule_removal()
        # end if
        if user_data.get('app'):
            app = user_data.pop('app')
            app.destroy()
            # remove output path
            #shutil.rmtree(app.output_path, ignore_errors=True)
        # end if
        update.message.reply_text(
            'Session closed',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    # end def

    def init_app(self, bot, update, user_data):
        if user_data.get('app'):
            self.destroy_app(bot, update, user_data)
        # end def

        app = App()
        app.initialize()
        user_data['app'] = app
        update.message.reply_text('A new session is created.')

        update.message.reply_text(
            'I recognize input of these two categories:\n'
            '- Profile page url of a lightnovel.\n'
            '- A query to search your lightnovel.\n'
            'Enter whatever you want or send /cancel to stop.'
        )
        return 'handle_novel_url'
    # end def

    def handle_novel_url(self, bot, update, user_data):
        if user_data.get('job'):
            app = user_data.get('app')
            job = user_data.get('job')
            update.message.reply_text(
                '%s\n'
                '%d out of %d chapters has been downloaded.\n'
                'To terminate this session send /cancel.'
                % (user_data.get('status'), app.progress, len(app.chapters))
            )
        else:
            if user_data.get('app'):
                app = user_data.get('app')
            else:
                app = App()
                app.initialize()
                user_data['app'] = app
            # end if
            app.user_input = update.message.text.strip()

            try:
                app.init_search()
            except Exception:
                update.message.reply_text(
                    'Sorry! I only recognize these sources:\n' +
                    'https://github.com/dipu-bd/lightnovel-crawler#supported-sources'
                )
                update.message.reply_text(
                    'Enter something again or send /cancel to stop.')
                return 'handle_novel_url'
            # end try

            if app.crawler:
                update.message.reply_text('Got your page link')
                return self.get_novel_info(bot, update, user_data)
            # end if

            if len(app.user_input) < 5:
                update.message.reply_text(
                    'Please enter a longer query text (at least 5 letters).')
                return 'handle_novel_url'
            # end if

            update.message.reply_text('Got your query text')
            return self.show_crawlers_to_search(bot, update, user_data)
        # end if
    # end def

    def show_crawlers_to_search(self, bot, update, user_data):
        app = user_data.get('app')

        buttons = []

        def make_button(i, url):
            return '%d - %s' % (i + 1, urlparse(url).hostname)
        # end def
        for i in range(1, len(app.crawler_links) + 1, 2):
            buttons += [[
                make_button(i - 1, app.crawler_links[i - 1]),
                make_button(i, app.crawler_links[i]) if i < len(
                    app.crawler_links) else '',
            ]]
        # end for

        update.message.reply_text(
            'Choose where to search for your novel, \n'
            'or send /skip to search everywhere.',
            reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True),
        )
        return 'handle_crawler_to_search'
    # end def

    def handle_crawler_to_search(self, bot, update, user_data):
        app = user_data.get('app')

        link = update.message.text
        if link:
            selected_crawlers = []
            if link.isdigit():
                selected_crawlers += [
                    app.crawler_links[int(link) - 1]
                ]
            else:
                selected_crawlers += [
                    x for i, x in enumerate(app.crawler_links)
                    if '%d - %s' % (i + 1, urlparse(x).hostname) == link
                ]
            # end if
            if len(selected_crawlers) != 0:
                app.crawler_links = selected_crawlers
            # end if
        # end if

        update.message.reply_text(
            'Searching for "%s" in %d sites. Please wait.' % (
                app.user_input, len(app.crawler_links)),
            reply_markup=ReplyKeyboardRemove(),
        )
        update.message.reply_text(
            'DO NOT type anything until I reply.\n'
            'You can only send /cancel to stop this session.'
        )

        app.search_novel()
        return self.show_novel_selection(bot, update, user_data)
    # end def

    def show_novel_selection(self, bot, update, user_data):
        app = user_data.get('app')

        if len(app.search_results) == 0:
            update.message.reply_text(
                'No results found by your query.\n'
                'Try again or send /cancel to stop.'
            )
            return 'handle_novel_url'
        # end if

        if len(app.search_results) == 1:
            user_data['selected'] = app.search_results[0]
            return self.show_source_selection(bot, update, user_data)
        # end if

        update.message.reply_text(
            'Choose any one of the following novels,' +
            ' or send /cancel to stop this session.',
            reply_markup=ReplyKeyboardMarkup([
                [
                    '%d. %s (in %d sources)' % (
                        index + 1, res['title'], len(res['novels'])
                    )
                ] for index, res in enumerate(app.search_results)
            ], one_time_keyboard=True),
        )

        return 'handle_select_novel'
    # end def

    def handle_select_novel(self, bot, update, user_data):
        app = user_data.get('app')

        selected = None
        text = update.message.text
        if text:
            if text.isdigit():
                selected = app.search_results[int(text) - 1]
            else:
                for i, item in enumerate(app.search_results[:10]):
                    sample = '%d. %s' % (i + 1, item['title'])
                    if text.startswith(sample):
                        selected = item
                    elif len(text) >= 5 and text.lower() in item['title'].lower():
                        selected = item
                    else:
                        continue
                    # end if
                    break
                # end for
            # end if
        # end if

        if not selected:
            return self.show_novel_selection(bot, update, user_data)
        # end if

        user_data['selected'] = selected
        return self.show_source_selection(bot, update, user_data)
    # end def

    def show_source_selection(self, bot, update, user_data):
        app = user_data.get('app')
        selected = user_data.get('selected')

        if len(selected['novels']) == 1:
            app.init_crawler(selected['novels'][0]['url'])
            return self.get_novel_info(bot, update, user_data)
        # end if

        update.message.reply_text(
            ('Choose a source to download "%s", ' % selected['title']) +
            'or send /cancel to stop this session.',
            reply_markup=ReplyKeyboardMarkup([
                [
                    '%d. %s %s' % (
                        index + 1,
                        novel['url'],
                        novel['info'] if 'info' in novel else ''
                    )
                ] for index, novel in enumerate(selected['novels'])
            ], one_time_keyboard=True),
        )

        return 'handle_select_source'
    # end def

    def handle_select_source(self, bot, update, user_data):
        app = user_data.get('app')
        selected = user_data.get('selected')

        source = None
        text = update.message.text
        if text:
            if text.isdigit():
                source = selected['novels'][int(text) - 1]
            else:
                for i, item in enumerate(selected['novels']):
                    sample = '%d. %s' % (i + 1, item['url'])
                    if text.startswith(sample):
                        source = item
                    elif len(text) >= 5 and text.lower() in item['url'].lower():
                        source = item
                    else:
                        continue
                    # end if
                    break
                # end for
            # end if
        # end if

        if not selected:
            return self.show_source_selection(bot, update, user_data)
        # end if

        app.init_crawler(source['url'])
        return self.get_novel_info(bot, update, user_data)
    # end def

    def get_novel_info(self, bot, update, user_data):
        app = user_data.get('app')
        user = update.message.from_user

        update.message.reply_text(app.crawler.novel_url)

        # TODO: Implement login feature. Create login_info_dict of (email, password)
        # if app.can_do('login'):
        #     app.login_data = login_info_dict.get(app.crawler.home_url)
        # # end if

        update.message.reply_text('Reading novel info...')
        app.get_novel_info()

        if os.path.exists(app.output_path):
            update.message.reply_text(
                'Local cache found do you want to use it',
                reply_markup=ReplyKeyboardMarkup([
                    ['Yes', 'No']
                ], one_time_keyboard=True),
            )
            return 'handle_delete_cache'
        else:
            os.makedirs(app.output_path, exist_ok=True)
            # Get chapter range
            update.message.reply_text(
                '%d volumes and %d chapters found.' % (
                    len(app.crawler.volumes),
                    len(app.crawler.chapters)
                ),
                reply_markup=ReplyKeyboardRemove()
            )
            return self.display_range_selection_help(bot, update)
        # end if
    # end def

    def handle_delete_cache(self, bot, update, user_data):
        app = user_data.get('app')
        user = update.message.from_user
        text = update.message.text
        if text.startswith('No'):
            if os.path.exists(app.output_path):
                shutil.rmtree(app.output_path, ignore_errors=True)
            os.makedirs(app.output_path, exist_ok=True)
            # end if
        # end if

        # Get chapter range
        update.message.reply_text(
            '%d volumes and %d chapters found.' % (
                len(app.crawler.volumes),
                len(app.crawler.chapters)
            ),
            reply_markup=ReplyKeyboardRemove()
        )
        return self.display_range_selection_help(bot, update)
    # end def

    def display_range_selection_help(self, bot, update):
        update.message.reply_text('\n'.join([
            'Send /all to download everything.',
            'Send /last to download last 50 chapters.',
            'Send /first to download first 50 chapters.',
            'Send /volume to choose specific volumes to download',
            'Send /chapter to choose a chapter range to download',
            'To tereminate this session, send /cancel.'
        ]))
        return 'handle_range_selection'
    # end def

    def range_selection_done(self, bot, update, user_data):
        app = user_data.get('app')
        update.message.reply_text(
            'You have selected %d chapters to download' % len(app.chapters)
        )
        if len(app.chapters) == 0:
            return self.display_range_selection_help(bot, update)
        # end if
        update.message.reply_text(
            'Do you want to generate a single file or split the books into volumes?',
            reply_markup=ReplyKeyboardMarkup([
                ['Single file', 'Split by volumes']
            ], one_time_keyboard=True),
        )
        return 'handle_pack_by_volume'
    # end def

    def handle_range_all(self, bot, update, user_data):
        app = user_data.get('app')
        app.chapters = app.crawler.chapters[:]
        return self.range_selection_done(bot, update, user_data)
    # end def

    def handle_range_first(self, bot, update, user_data):
        app = user_data.get('app')
        app.chapters = app.crawler.chapters[:50]
        return self.range_selection_done(bot, update, user_data)
    # end def

    def handle_range_last(self, bot, update, user_data):
        app = user_data.get('app')
        app.chapters = app.crawler.chapters[-50:]
        return self.range_selection_done(bot, update, user_data)
    # end def

    def handle_range_volume(self, bot, update, user_data):
        app = user_data.get('app')
        buttons = [str(vol['id']) for vol in app.crawler.volumes]
        update.message.reply_text(
            'I got these volumes: ' + ', '.join(buttons) +
            '\nEnter which one these volumes you want to download separated space or commas.'
        )
        return 'handle_volume_selection'
    # end def

    def handle_volume_selection(self, bot, update, user_data):
        app = user_data.get('app')

        text = update.message.text
        selected = re.findall(r'\d+', text)
        update.message.reply_text(
            'Got the volumes: ' + ', '.join(selected),
        )

        selected = [int(x) for x in selected]
        app.chapters = [
            chap for chap in app.crawler.chapters
            if selected.count(chap['volume']) > 0
        ]
        return self.range_selection_done(bot, update, user_data)
    # end def

    def handle_range_chapter(self, bot, update, user_data):
        app = user_data.get('app')
        chapters = app.crawler.chapters
        update.message.reply_text(
            'I got %s  chapters' % len(chapters) +
            '\nEnter which start and end chapter you want to generate separated space or comma.',
        )
        return 'handle_chapter_selection'
    # end def

    def handle_chapter_selection(self, bot, update, user_data):
        app = user_data.get('app')
        text = update.message.text
        selected = re.findall(r'\d+', text)
        print(selected)
        if len(selected) != 2:
            update.message.reply_text(
                'Sorry, I did not understand. Please try again')
            return 'handle_range_chapter'
        else:
            selected = [int(x) for x in selected]
            app.chapters = app.crawler.chapters[selected[0]-1:selected[1]]
            update.message.reply_text(
                'Got the start chapter : %s' % selected[0] +
                '\nThe end chapter : %s' % selected[1] +
                '\nTotal chapter chosen is %s' % len(app.chapters),
            )
        return self.range_selection_done(bot, update, user_data)
    # end def

    def handle_pack_by_volume(self, bot, update, user_data):
        app = user_data.get('app')

        text = update.message.text
        app.pack_by_volume = text.startswith('Split')

        if app.pack_by_volume:
            update.message.reply_text(
                'I will split output files into volumes')
        else:
            update.message.reply_text(
                'I will generate single output files whenever possible')
        # end if

        i = 0
        new_list = [['all']]
        while i < len(available_formats):
            new_list.append(available_formats[i:i+2])
            i += 2

        update.message.reply_text(
            'In which format you want me to generate your book?',
            reply_markup=ReplyKeyboardMarkup(
                new_list,
                one_time_keyboard=True,
            ),
        )

        return 'handle_output_format'
    # end def

    def handle_output_format(self, bot, update, job_queue, user_data):
        app = user_data.get('app')
        user = update.message.from_user

        text = update.message.text.strip().lower()
        app.output_formats = {}
        if text in available_formats:
            for x in available_formats:
                if x == text:
                    app.output_formats[x] = True
                else:
                    app.output_formats[x] = False
                # end if
            # end for
        elif text != 'all':
            update.message.reply_text('Sorry, I did not understand.')
            return
        # end if

        job = job_queue.run_once(
            self.process_download_request,
            1,
            context=(update, user_data),
            name=str(user.id),
        )
        user_data['job'] = job

        update.message.reply_text(
            'Your request has been received.'
            'I will generate book in "%s" format' % text,
            reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END
    # end def

    def process_download_request(self, bot, job):
        update, user_data = job.context

        app = user_data.get('app')
        if app:
            user_data['status'] = 'Downloading "%s"' % app.crawler.novel_title
            app.start_download()
            update.message.reply_text('Download finished.')
        # end if

        app = user_data.get('app')
        if app:
            user_data['status'] = 'Generating output files'
            update.message.reply_text(user_data.get('status'))
            output_files = app.bind_books()
            update.message.reply_text('Output files generated.')
        # end if

        app = user_data.get('app')
        if app:
            user_data['status'] = 'Compressing output folder.'
            update.message.reply_text(user_data.get('status'))
            app.compress_books()
        # end if

        for archive in app.archived_outputs:
            file_size = os.stat(archive).st_size
            if file_size < 49.99 * 1024 * 1024:
                update.message.reply_document(
                    open(archive, 'rb'),
                    timeout=24 * 3600,  # 24 hours
                )
            else:
                update.message.reply_text(
                    'File size more than 50 MB so cannot be sent via telegram bot.\n' +
                    'Uploading to alternative cloud storage')
                try:
                    description = 'Generated By : Lightnovel Crawler Telegram Bot'
                    direct_link = upload(archive, description)
                    update.message.reply_text('Get your file here: %s' % direct_link)
                except Exception as e:
                    logger.error('Failed to upload file: %s', archive, e)
                # end try
            # end if
        # end for

        self.destroy_app(bot, update, user_data)
    # end def

    def handle_downloader(self, bot, update, user_data):
        app = user_data.get('app')
        job = user_data.get('job')

        if app or job:
            update.message.reply_text(
                '%s\n'
                '%d out of %d chapters has been downloaded.\n'
                'To terminate this session send /cancel.'
                % (user_data.get('status'), app.progress, len(app.chapters))
            )
        # else:
        #     self.show_help(bot, update)
        # end if

        return ConversationHandler.END
    # end def
# end class
