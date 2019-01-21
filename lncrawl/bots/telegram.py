#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from ..core.app import App
from ..utils.bot_interface import BotInterface

logger = logging.getLogger(__name__)


class TelegramBot(BotInterface):
    def start(self):
        # Create the EventHandler and pass it your bot's token.
        updater = Updater(os.getenv('TELEGRAM_TOKEN', ''))

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # Add conversation handler with the states SUMBER, PHOTO, LOCATION and BIO
        conv_handler = ConversationHandler(
            entry_points=[ CommandHandler('start', start) ],
            states={
                'get_novel_url': [ MessageHandler(Filters.text, get_novel_url) ],
            },
            fallbacks=[CommandHandler('cancel', stop)]
        )
        dp.add_handler(conv_handler)

        # Log all errors
        dp.add_error_handler(handle_error)

        help_handler = CommandHandler('help', show_help)
        dp.add_handler(help_handler)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
    # end def

    def create_app(self):
        # TODO: must be implemented
        self.app = App()
        self.app.initialize()
        # Start processing using this bot. It should use self methods to take
        # inputs and self.app methods to process them.

        # Here is a sample algorithm
        '''
        self.app.user_input = self.get_novel_url()
        self.app.init_search()

        self.app.crawler_links = self.get_crawlers_to_search()
        self.app.search_novel()

        self.app.init_crawler(self.choose_a_novel())

        if self.app.can_login:
            self.app.login_data = self.get_login_info()
        # end if

        self.app.get_novel_info()

        self.app.output_path = self.get_output_path()
        self.app.chapters = self.process_chapter_range()

        self.app.output_formats = self.get_output_formats()
        self.app.pack_by_volume = self.should_pack_by_volume()
        if self.app.output_formats['mobi']:
            self.app.fetch_kindlegen = self.should_fetch_kindlegen()
        # end if

        self.app.start_download()
        self.app.bind_books()
        '''
    # end def

    def get_novel_url(self):
        '''Returns a novel page url or a query'''
        # TODO: must be implemented
        pass
    # end def

    def get_crawlers_to_search(self, links):
        '''Returns user choice to search the choosen sites for a novel'''
        # TODO: must be implemented
        pass
    # end def

    def choose_a_novel(self, search_results):
        '''Choose a single novel url from the search result'''
        # The search_results is an array of (novel_title, novel_url).
        # This method should return a single novel_url only
        #
        # By default, returns the first search_results. Implemented it to
        # handle multiple search_results
        pass
    # end def

    def get_output_path(self, suggested_path):
        '''Returns a valid output path where the files are stored'''
        # You should return a valid absolute path. The parameter suggested_path
        # is valid but not gurranteed to exists.
        # 
        # NOTE: If you do not want to use any pre-downloaded files, remove all
        #       contents inside of your selected output directory.
        #
        # By default, returns a valid existing path from suggested_path
        pass
    # end def

    def get_output_formats(self):
        '''Returns a dictionary of output formats.'''
        # The keys should be from from `self.output_formats`. Each value
        # corresponding a key defines whether create output in that format.
        #
        # By default, it returns all True to all of the output formats.
        pass
    # end def

    def get_login_info(self):
        '''Returns the (email, password) pair for login'''
        # By default, returns None to skip login
        pass
    # end if

    def get_range_selection(self, chapter_count, volume_count):
        '''Returns a choice of how to select the range of chapters to downloads'''
        # TODO: must be implemented
        # Should return a key from `self.selections` array
        pass
    # end def

    def get_range_using_urls(self, crawler):
        '''Returns a range of chapters using start and end urls as input'''
        # TODO: must be implemented
        # Should return a list of chapters to download
        pass
    # end def

    def get_range_using_index(self, chapter_count):
        '''Returns a range selected using chapter indices'''
        # TODO: must be implemented
        # Should return a list of chapters to download
        pass
    # end def

    def get_range_from_volumes(self, volumes, times=0):
        '''Returns a range created using volume list'''
        # TODO: must be implemented
        # Should return a list of chapters to download
        pass
    # end def

    def get_range_from_chapters(self, crawler, times=0):
        '''Returns a range created using individual chapters'''
        # TODO: must be implemented
        # Should return a list of chapters to download
        pass
    # end def

    def should_pack_by_volume(self):
        '''Returns whether to generate single or multiple files by volumes'''
        # By default, returns False to generate a single file
        pass
    # end def

    def should_fetch_kindlegen(self):
        '''Whether to fetch kindlegen if it does not exists'''
        # By default, returns True to download kindlegen in the user directory to use it
        pass
    # end def
# end class
