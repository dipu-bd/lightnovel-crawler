# -*- coding: utf-8 -*-
import logging
import logging.config
import os
import random
import subprocess
from datetime import datetime

import discord

from ...core.arguments import get_args
from .config import signal
from .message_handler import MessageHandler

logger = logging.getLogger(__name__)


def get_bot_version():
    try:
        result = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'])
        return result.decode('utf-8')
    except:
        from lncrawl.assets import version
        return version.get_value()


class DiscordBot(discord.Client):
    bot_version = get_bot_version()

    def __init__(self, *args, loop=None, **options):
        options['shard_id'] = get_args().shard_id
        options['shard_count'] = get_args().shard_count
        options['heartbeat_timeout'] = 300
        options['guild_subscriptions'] = False
        options['fetch_offline_members'] = False
        super().__init__(*args, loop=loop, **options)
    # end def

    def start_bot(self):
        self.bot_is_ready = False
        os.environ['debug_mode'] = 'yes'
        self.run(os.getenv('DISCORD_TOKEN'))
    # end def

    async def on_ready(self):
        # Reset handler cache
        self.handlers = {}

        print('Discord bot in online!')
        activity = discord.Activity(name='for 🔥%s🔥 (%s)' % (signal, self.bot_version),
                                    type=discord.ActivityType.watching)
        await self.change_presence(activity=activity,
                                   status=discord.Status.online)

        self.bot_is_ready = True
    # end def

    async def on_message(self, message):
        if not self.bot_is_ready:
            return  # Not ready yet
        if message.author == self.user:
            return  # I am not crazy to talk with myself
        if message.author.bot:
            return  # Other bots are not edible
        try:
            # Cleanup unused handlers
            self.cleanup_handlers()

            text = message.content
            if isinstance(message.channel, discord.abc.PrivateChannel):
                await self.handle_message(message)
            elif text.startswith(signal) and len(text.split(signal)) == 2:
                uid = message.author.id
                if uid in self.handlers:
                    self.handlers[uid].destroy()
                # end if
                await self.send_public_text(message, random.choice([
                    "Sending you a private message",
                ]))
                await self.handle_message(message)
            # end if
        except IndexError as ex:
            logger.exception('Index error reported', ex)
        except Exception:
            logger.exception('Something went wrong processing message')
        # end try
    # end def

    async def send_public_text(self, message, text):
        async with message.channel.typing():
            await message.channel.send(text + (" <@%s>" % str(message.author.id)))
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

    def cleanup_handlers(self):
        try:
            cur_time = datetime.now()
            for handler in self.handlers.values():
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
