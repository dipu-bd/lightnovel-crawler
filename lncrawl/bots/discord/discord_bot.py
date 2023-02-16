import discord

import redis.asyncio as redis

from . import config as C


class Bot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.redis = redis.from_url(url=C.redis_uri)
        self.load_extension("lncrawl.bots.discord.cogs.novels")

    async def on_ready(self):
        print(f"{self.user} is ready and online!")
        print(f"Redis ping successful: {await self.redis.ping()}")

    def get_redis(self):
        return self.redis


client = Bot()
client.run(C.discord_token)
