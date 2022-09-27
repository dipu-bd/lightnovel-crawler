import os
import subprocess
from datetime import datetime
from typing import Dict

import discord

from . import config as C
from .config import logger
from .message_handler import MessageHandler


def get_bot_version():
    try:
        result = subprocess.check_output(["git", "rev-list", "--count", "HEAD"])
        return result.decode("utf-8")
    except Exception:
        from lncrawl.assets import version

        return version.get_version()


class DiscordBot(discord.Client):
    bot_version = get_bot_version()

    def __init__(self, *args, loop=None, **options):
        options["shard_id"] = C.shard_id
        options["shard_count"] = C.shard_count
        options["heartbeat_timeout"] = 300
        options["guild_subscriptions"] = False
        options["fetch_offline_members"] = False
        self.handlers: Dict[str, MessageHandler] = {}
        super().__init__(*args, loop=loop, **options)

    def start_bot(self):
        self.bot_is_ready = False
        os.environ["debug_mode"] = "yes"
        self.run(C.discord_token)

    async def on_ready(self):
        # Reset handler cache
        self.handlers = {}

        print("Discord bot in online!")
        activity = discord.Activity(
            name="for 🔥%s🔥 (%s)" % (C.signal, self.bot_version),
            type=discord.ActivityType.watching,
        )
        await self.change_presence(activity=activity, status=discord.Status.online)

        self.bot_is_ready = True

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
            elif text.startswith(C.signal) and len(text.split(C.signal)) == 2:
                uid = str(message.author.id)
                async with message.channel.typing():
                    await message.channel.send(
                        f"Sending you a private message <@{uid}>"
                    )
                if uid in self.handlers:
                    self.handlers[uid].destroy()

                await self.handle_message(message)

        except IndexError as ex:
            logger.exception("Index error reported", ex)
        except Exception:
            logger.exception("Something went wrong processing message")

    async def handle_message(self, message):
        if self.is_closed():
            return

        try:
            uid = str(message.author.id)
            discriminator = message.author.discriminator
            logger.info(
                "Processing message from %s#%s", message.author.name, discriminator
            )
            if uid in self.handlers:
                self.handlers[uid].process(message)
            # elif len(self.handlers) > C.max_active_handles or discriminator not in C.vip_users_ids:
            #     async with message.author.typing():
            #         await message.author.send(
            #             "Sorry! I am too busy processing requests of other users.\n"
            #             "Please knock again in a few hours."
            #         )
            else:
                logger.info(
                    "New handler for %s#%s [%s]",
                    message.author.name,
                    discriminator,
                    uid,
                )
                self.handlers[uid] = MessageHandler(uid, self)
                async with message.author.typing():
                    await message.author.send(
                        "-" * 25 + "\n" + f"Hello <@{uid}>\n" + "-" * 25 + "\n"
                    )
                self.handlers[uid].process(message)

        except Exception:
            logger.exception("While handling this message: %s", message)

    def cleanup_handlers(self):
        try:
            cur_time = datetime.now()
            for handler in self.handlers.values():
                if handler.is_busy():
                    continue

                last_time = getattr(handler, "last_activity", cur_time)
                if (cur_time - last_time).seconds > C.session_retain_time_in_seconds:
                    handler.destroy()

        except Exception:
            logger.exception("Failed to cleanup handlers")
