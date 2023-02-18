import logging
import discord

from . import config as C

logger = logging.getLogger(__name__)


class Bot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.load_extension("lncrawl.bots.discord.cogs.novels")

    async def on_ready(self):
        # todo: activity and stuff
        logger.debug(f"{self.user} is ready and online!")


client = Bot()
client.run(C.discord_token)
