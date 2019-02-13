#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
import os
import shutil
from urllib.parse import urlparse

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, ConversationHandler, Filters, Handler,
                          MessageHandler, RegexHandler, Updater)

from ..core.app import App
from ..spiders import crawler_list
from ..binders import available_formats
from ..utils.uploader import upload

logger = logging.getLogger('TELEGRAM_BOT')


class TelegramBot:
    def start(self):
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
            ],
            fallbacks=[
                CommandHandler('cancel', self.destroy_app, pass_user_data=True),
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
                'initialize_crawler': [
                    MessageHandler(
                        Filters.text, self.initialize_crawler, pass_user_data=True),
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
                        'chapter', self.handle_range_chapter, pass_user_data = True),
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
        dp.add_handler(MessageHandler(Filters.text, self.handle_downloader, pass_user_data=True))

        # Log all errors
        dp.add_error_handler(self.error_handler)

        # Start the Bot
        self.updater.start_polling()

        logger.warn('Telegram bot is online!')

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
    # end def

    def error_handler(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Error: %s\nCaused by: %s', error, update)
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
            shutil.rmtree(app.output_path, ignore_errors=True)
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
        app = user_data.get('app')
        app.user_input = update.message.text.strip()

        try:
            app.init_search()
        except:
            update.message.reply_text(
                'Sorry! I only recognize these sources:\n' +
                '\n'.join(['- %s' % x for x in crawler_list.keys()]))
            update.message.reply_text(
                'Enter something again or send /cancel to stop.')
            return 'handle_novel_url'
        # end try

        if app.crawler:
            update.message.reply_text('Got your page link')
            return self.get_novel_info(bot, update, user_data)
        else:
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
            'Searching for your novel in %d sites.\n'
            'Please wait patiently or send /cancel to stop.' % len(app.crawler_links))

        app.search_novel()
        for i, (title, url) in enumerate(app.search_results):
            title = '%d. %s (%s)' % (i + 1, title, urlparse(url).hostname)
            app.search_results[i] = title, url
        # end def
        if len(app.search_results) < 2:
            return self.initialize_crawler(bot, update, user_data)
        else:
            buttons = [[title] for title, url in app.search_results]
            update.message.reply_text(
                'Choose your novel, or send /skip to choose the first one',
                reply_markup=ReplyKeyboardMarkup(
                    buttons, one_time_keyboard=True),
            )
            return 'initialize_crawler'
        # end if
    # end def

    def initialize_crawler(self, bot, update, user_data):
        app = user_data.get('app')

        # Resolve selected novel
        text = update.message.text
        novel_url = None
        for title, url in app.search_results:
            if text == title:
                novel_url = url
                break
            # end if
        # end for

        if not novel_url:
            if len(app.search_results) != 0:
                novel_url = app.search_results[0][1]
            # end if
        # end if

        if not novel_url:
            update.message.reply_text(
                'Sorry! No novels for your query.\n'
                'Enter something or send /cancel to stop.',
                reply_markup=ReplyKeyboardRemove(),
            )
            return 'handle_crawler_to_search'
        # end if

        app.init_crawler(novel_url)
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

        # Setup output path
        output_path = os.path.join('.telegram_bot_output', str(user.id))
        output_path = os.path.join(
            output_path, os.path.basename(app.output_path))
        output_path = os.path.abspath(output_path)
        if os.path.exists(output_path):
            shutil.rmtree(output_path, ignore_errors=True)
        # end if
        os.makedirs(output_path, exist_ok=True)
        app.output_path = output_path

        # Get chapter range
        update.message.reply_text(
            '%d volumes and %d chapters found.' % (
                len(app.crawler.volumes),
                len(app.crawler.chapters)
            )
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
            'I got %s  chapters' %len(chapters) +
            '\nEnter which start and end chapter you want to generate separated space or comma.',
        )
        return 'handle_chapter_selection'
    # end def

    def handle_chapter_selection(self, bot, update, user_data):
        app = user_data.get('app')
        text = update.message.text
        selected = re.findall(r'\d+', text)
        print(selected)
        if len(selected)!=2:
            update.message.reply_text('Sorry, I did not understand. Please try again')
            return 'handle_range_chapter'
        else: 
            selected = [int(x) for x in selected]
            app.chapters = app.crawler.chapters[selected[0]-1:selected[1]]
            update.message.reply_text(
                'Got the start chapter : %s' %selected[0] +
                '\nThe end chapter : %s' %selected[1] +
                '\nTotal chapter chosen is %s' %len(app.chapters),
            )
        return self.range_selection_done(bot, update, user_data)
    # end def

    def handle_pack_by_volume(self, bot, update, user_data):
        app = user_data.get('app')
        user = update.message.from_user

        text = update.message.text
        app.pack_by_volume = text.startswith('Split')

        if app.pack_by_volume:
            update.message.reply_text(
                'I will split output files into volumes')
        else:
            update.message.reply_text(
                'I will generate single output files whenever possible')
        # end if

        i=0
        new_list = [['all']]
        while i<len(available_formats):
            new_list.append(available_formats[i:i+2])
            i+=2
            
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
                if x == text :
                    app.output_formats[x] = True
                else:
                    app.output_formats[x] = False
                # end if 
            # end for
        elif text != 'all':
            update.message.reply_text('Sorry, I did not understand.')
            return
        #end if

        job = job_queue.run_once(
            self.process_request,
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


    def process_request(self, bot, job):
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
            output = app.bind_books()
            update.message.reply_text('Output file generated.')
        # end if

        app = user_data.get('app')
        if app:
            user_data['status'] = 'Compressing output folder.'
            update.message.reply_text(user_data.get('status'))
            app.compress_output()
        # end if


        for archive in app.archived_outputs:
            link_id = upload(archive)
            if link_id:
                update.message.reply_text(
                    'Get your file here:'
                    'https://drive.google.com/open?id=%s' % link_id
                )
            else:
                update.message.reply_document(
                    open(archive, 'rb'),
                    timeout=24 * 3600, # 24 hours
                )
                update.message.reply_text(
                    'This file will be available for 24 hours to download')
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
        else:
            self.show_help(bot, update)
        # end if

        return ConversationHandler.END
    # end def
# end class
