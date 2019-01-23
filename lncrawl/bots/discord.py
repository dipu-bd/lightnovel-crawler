#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
import asyncio
import discord

from ..core.app import App

logger = logging.getLogger('DISCORD_BOT')

class MessageHandler:
    def __init__(self, client):
        self.app = App()
        self.client = client
    # end def

    def destory(self):
        self.app.destroy()
    # end def

    async def process(self, message):
        self.message = message
        self.user = message.user
    # end def

    async def send(self, content):
        await self.client.send_message(self.user, content)
    # end def
# end class

class DiscordBot(discord.Client):
    # Store user message handlers
    handlers = dict()

    def start_bot(self):
        self.run(os.getenv('DISCORD_TOKEN'))
    # end def

    @asyncio.coroutine
    async def on_ready(self):
        logger.warn('Discord bot in online!')
        await self.change_presence(
            game=discord.Game(name="above the clouds")
        )
    # end def

    @asyncio.coroutine
    async def on_message(self, message):
        if message.author == self.user:
            return # To not to reply to myself
        # end if
        if message.author.bot:
            logger.debug('A bot asked something. Bot name is "%s"' % message.author)
            return # Bots are not edible
        # end if
        if message.channel.is_private:
            await self.handle_message(message)
        elif message.content == '!help':
            await self.public_help(message)
        elif message.content == '!lncrawl':
            await self.init_app(message)
        # end if
    # end def

    async def handle_message(self, message):
        user = message.author
        if self.handlers.get(user.id):
            await self.handlers.get(user.id).process(message)
        else:
            logger.debug('Could not find any handler for "%s"', message.channel)
        # end if
    # end def

    async def public_help(self, message):
        await self.send_message(
            message.channel,
            'Enter `!lncrawl` to start a new session of **Lightnovel Crawler**'
        )
    # end def

    async def init_app(self, message):
        user = message.author
        if not self.handlers.get(user.id):
            self.handlers[user.id] = MessageHandler(self)
        # end if
        await self.handle_message(message)
    # end def

    def destroy_app(self, message):
        user = message.author
        if self.handlers.get(user.id):
            self.handlers.pop(user.id).destroy()
        # end if
    # end def
# end def
