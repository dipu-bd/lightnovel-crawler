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
    # To save App instances against user id
    app = dict()

    def start(self):
        # Create the EventHandler and pass it your bot's token.
        self.updater = Updater(os.getenv('TELEGRAM_TOKEN', ''))

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # Add a command helper for help
        dp.add_handler(CommandHandler('help', self.show_help))

        # Add conversation handler with states
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.init_app)],
            fallbacks=[CommandHandler('cancel', self.destroy_app)],
            states={
                'get_novel_url': [MessageHandler(Filters.text, self.get_novel_url)],
                'get_crawlers_to_search': [MessageHandler(Filters.text, self.get_crawlers_to_search)],
                'choose_a_novel': [MessageHandler(Filters.text, self.choose_a_novel)],
                'get_login_info': [MessageHandler(Filters.text, self.get_login_info)],
                'get_output_path': [MessageHandler(Filters.text, self.get_output_path)],
                'process_chapter_range': [MessageHandler(Filters.text, self.process_chapter_range)],
                'get_output_formats': [MessageHandler(Filters.text, self.get_output_formats)],
                'should_pack_by_volume': [MessageHandler(Filters.text, self.should_pack_by_volume)],
            },
        )
        dp.add_handler(conv_handler)

        # Log all errors
        dp.add_error_handler(self.error_handler)

        # Start the Bot
        self.updater.start_polling()

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
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Type /start to create new session.\n'
                 'Type /cancel to cancel an ongoing session.\n'
                 'Type /progress to view progress of current session.\n'
                 'Type /help to view this message anytime.')
    # end def

    def init_app(self, bot, update):
        user = update.message.from_user
        if not self.app.get(user.id):
            self.app[user.id] = App()
            self.app[user.id].initialize()
            update.message.reply_text('A new session is created.')
        else:
            update.message.reply_text('Using an ongoing session.')
        # end if

        update.message.reply_text(
            'Enter a text from one of these two categories:\n'
            '- The profile page url of a lightnovel.\n'
            '- A query text to search your novel.'
        )
        return 'get_novel_url'
    # end def

    def destroy_app(self, bot, update):
        user = update.message.from_user
        if self.app.get(user.id):
            self.app.pop(user.id).destroy()
        # end if
        update.message.reply_text('Session is cancelled')
        return ConversationHandler.END
    # end def

    def get_novel_url(self, bot, update):
        user = update.message.from_user
    # end def

    def get_crawlers_to_search(self, bot, update):
        user = update.message.from_user
    # end def

    def choose_a_novel(self, bot, update):
        user = update.message.from_user
    # end def

    def get_output_path(self, bot, update):
        user = update.message.from_user
    # end def

    def get_output_formats(self, bot, update):
        user = update.message.from_user
    # end def

    def get_login_info(self, bot, update):
        user = update.message.from_user
    # end if

    def get_range_selection(self, bot, update):
        user = update.message.from_user
    # end def

    def process_chapter_range(self, bot, update):
        user = update.message.from_user
    # end def

    def get_range_using_urls(self, bot, update):
        user = update.message.from_user
    # end def

    def get_range_using_index(self, bot, update):
        user = update.message.from_user
    # end def

    def get_range_from_volumes(self, bot, update):
        user = update.message.from_user
    # end def

    def get_range_from_chapters(self, bot, update):
        user = update.message.from_user
    # end def

    def should_pack_by_volume(self, bot, update):
        user = update.message.from_user
    # end def
# end class
