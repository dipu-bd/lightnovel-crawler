import asyncio
import io
import math
import discord
import logging
import redis
from discord.ext import commands

from lncrawl.core.app import App

from ..components import NovelMenu
from ..utils import validate_formats
from ..config import available_formats
from ..novel_handlers import (
    archive_metadata,
    build_hash_novel_key,
    configure_output_path,
    get_hash_value,
    destroy_app,
    download_novel,
    novel_by_title,
    novel_by_url,
    upload_file,
    update_progress,
)

logger = logging.getLogger(__name__)


class Novels(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.redis: redis.Redis = self.bot.get_redis()

    @discord.slash_command(name="download", description="Download a novel by URL")
    @discord.option("url", description="Novel URL")
    @discord.option("start", description="Start chapter", default=0)
    @discord.option("end", description="End chapter", default=math.inf)
    @discord.option(
        "formats", description="Comma separated target formats", default="epub"
    )
    async def download(
        self,
        ctx: discord.ApplicationContext,
        url: str,
        start: float,
        end: float,
        formats: str,
    ):
        if not url.startswith("http"):
            await ctx.respond("You specified an invalid URL")
            return
        formats_list = list(map(str.strip, formats.split(",")))
        if not validate_formats(formats_list):
            fs = ", ".join(available_formats)
            await ctx.respond(
                f"The format you specified is invalid, the available formats are: {fs}"
            )
        # start thinking
        await ctx.defer()

        app: App = await novel_by_url(url)
        embed = discord.Embed(
            title=app.crawler.novel_title,
            url=app.crawler.novel_url,
            description=app.crawler.novel_synopsis,
        )
        embed.set_thumbnail(url=app.crawler.novel_cover)
        embed.add_field(name="Author", value=app.crawler.novel_author, inline=False)
        embed.add_field(name="Volumes", value=len(app.crawler.volumes))
        embed.add_field(name="Chapters", value=len(app.crawler.chapters))
        await ctx.respond(embed=embed)

        # check if we have this cached
        # todo: use HKEYS and check if there are other sources, propose those to the user
        existingFiles = {
            k: await get_hash_value(
                redis=self.redis,
                hash=build_hash_novel_key(app, start, end, k),
                source=app.good_source_name,
            )
            for k in formats_list
        }
        for fmt, cachedUrl in existingFiles.items():
            if not cachedUrl:
                continue
            logger.debug("format %s exists: %s", fmt, cachedUrl)
            formats_list.remove(fmt)
            await ctx.respond(f"**{fmt}**: {cachedUrl}")

        if not formats_list:
            logger.debug("no formats left to dl, returning")
            await destroy_app(app)
            return

        # set chapters
        if math.isinf(end):
            app.chapters = app.crawler.chapters[int(start) :]
        else:
            app.chapters = app.crawler.chapters[int(start) : int(end)]

        followUp = await ctx.respond(
            f"I don't have this file, downloading {len(app.chapters)} chapters, this will take a while."
        )

        # set formats
        app.output_formats = {x: (x in formats_list) for x in available_formats}
        # set up directories
        app.output_path = configure_output_path(app)
        # update the user with dl progress
        progress_report = update_progress(app, followUp.edit)
        asyncio.create_task(progress_report)

        # start the download
        archive_list = await download_novel(app)

        try:
            for archive in archive_list:
                archive_format, archive_name = archive_metadata(archive)
                result = await upload_file(archive)
                if isinstance(result, str):
                    await ctx.respond(f"Download URL: {result}")
                elif isinstance(result, io.BufferedReader):
                    fileResponse = await ctx.respond(
                        file=discord.File(filename=archive_name, fp=result)
                    )
                    attachment, *_ = fileResponse.attachments
                    # files:novel_name:1_12329:fb2 source_name https://source
                    await self.redis.hset(
                        name=build_hash_novel_key(app, start, end, archive_format),
                        key=app.good_source_name,
                        value=attachment.url,
                    )
                else:
                    await ctx.respond(f"Failed to upload {archive_name}")
        finally:
            await destroy_app(app)

    @discord.slash_command(name="search", description="Search a novel by name")
    @discord.option("name", description="Lightnovel name")
    @discord.option("pattern", description="Regex pattern", default="")
    async def search(
        self,
        ctx: discord.ApplicationContext,
        name: str,
        pattern: str,
    ):
        if len(name) < 4:
            await ctx.respond("Query string is too short")
            return
        # start thinking
        await ctx.defer()
        app: App = await novel_by_title(name, pattern)
        # app.search_results
        selectNovelView = NovelMenu()
        selectNovelView.add_items(novelList=app.search_results[:24])
        await ctx.respond(
            "Select a novel, use the returned link in the `/download` command",
            view=selectNovelView,
        )


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Novels(bot))  # add the cog to the bot
