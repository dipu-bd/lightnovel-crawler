# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import queue
import re
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import discord

from ...binders import available_formats
from ...core.app import App
from ...sources import crawler_list
from ...utils.uploader import upload
from .config import signal
from .message_handler import MessageHandler

logger = logging.getLogger('DISCORD_BOT')


class DiscordBot(discord.Client):
    handlers = {}

    def start_bot(self):
        self.run(os.getenv('DISCORD_TOKEN'))
    # end def

    async def on_ready(self):
        print('Discord bot in online!')
        activity = discord.Activity(name='🔥%slncrawl🔥' % signal,
                                    type=discord.ActivityType.watching)
        await self.change_presence(activity=activity,
                                   status=discord.Status.online)
    # end def

    async def on_message(self, message):
        self.cleanup_handlers()
        if message.author == self.user:
            return  # I am not crazy to talk with myself
        # end if
        if message.author.bot:
            return  # Other bots are not edible
        # end if
        try:
            if message.content == signal + 'lncrawl':
                uid = message.author.id
                if uid in self.handlers:
                    self.handlers[uid].destroy()
                # end if
                await self.handle_message(message)
            elif isinstance(message.channel, discord.abc.PrivateChannel):
                await self.handle_message(message)
            # end if
        except Exception:
            logger.exception('Something went wrong processing message')
        # end try
    # end def

    async def send_public_text(self, message, text):
        async with message.channel.typing():
            await message.channel.send(text)
    # end def

    async def handle_message(self, message):
        if self.is_closed():
            return
        # end if
        try:
            uid = str(message.author.id)
            logger.info("Processing message from %s", message.author.name)
            if uid not in self.handlers:
                self.handlers[uid] = MessageHandler(self)
                await message.author.send(
                    '-' * 25 + '\n' +
                    ('Hello %s\n' % message.author.name) +
                    '-' * 25 + '\n'
                )
                logger.info("New handler for %s", message.author.name)
            # end if
            self.handlers[uid].process(message)
        except Exception as err:
            logger.exception('While handling this message: %s', message)
        # end try
    # end def

    async def cleanup_handlers(self):
        try:
            cur_time = datetime.now()
            for uid, handler in self.handlers.items():
                last_time = getattr(handler, 'last_activity', cur_time)
                if (cur_time - last_time).days > 1:
                    handler.destroy()
                # end if
            # end for
        except Exception:
            logger.exception('Failed to cleanup handlers')
        # end try
    # end def
# end class
