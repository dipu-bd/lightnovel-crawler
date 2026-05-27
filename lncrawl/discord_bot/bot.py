from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from ..context import ctx

logger = logging.getLogger(__name__)

STATUS_EMOJI = {
    0: "⏳",
    1: "🔄",
    2: "✅",
    3: "❌",
    4: "🚫",
}


def _run_crawl_sync(url: str, range_spec: str, fmt: str, max_size_mb: float) -> dict:
    from ..enums import OutputFormat
    from .file_upload import get_file_delivery

    ctx.setup()
    ctx.sources.ensure_load()
    user = ctx.users.get_admin()
    crawler = ctx.sources.init_crawler(url)

    if getattr(crawler, "can_login", False):
        logger.warning("Source supports login but Discord bot does not provide credentials")

    novel = ctx.crawler.fetch_novel(user.id, url, crawler=crawler)

    if novel.chapter_count == 0:
        return {"error": "No chapters to download"}

    range_lower = range_spec.lower().strip()
    range_last = None
    range_first = None
    if range_lower.startswith("last"):
        parts = range_lower.split()
        try:
            range_last = int(parts[1]) if len(parts) > 1 else 10
        except (ValueError, IndexError):
            return {"error": "Invalid range: expected a number after 'last'"}
    elif range_lower.startswith("first"):
        parts = range_lower.split()
        try:
            range_first = int(parts[1]) if len(parts) > 1 else 10
        except (ValueError, IndexError):
            return {"error": "Invalid range: expected a number after 'first'"}

    chapters = ctx.chapters.list_ids(
        novel_id=novel.id,
        descending=bool(range_last),
        limit=range_last or range_first,
    )
    if not chapters:
        return {"error": "No chapters found for the given range"}

    chapter_futures = [
        crawler.taskman.submit_task(
            ctx.crawler.fetch_chapter,
            user.id,
            chapter_id,
            crawler=crawler,
        )
        for chapter_id in sorted(set(chapters))
    ]
    chapter_image_ids = []
    for chapter in crawler.taskman.resolve(chapter_futures, desc="Chapters", unit=" c"):
        if not chapter:
            continue
        chapter_image_ids += ctx.images.list_ids(chapter_id=chapter.id)

    image_futures = [
        crawler.taskman.submit_task(
            ctx.crawler.fetch_image,
            user.id,
            image_id,
            crawler=crawler,
        )
        for image_id in sorted(set(chapter_image_ids))
    ]
    crawler.taskman.resolve_futures(image_futures, desc="Images", unit=" img")

    try:
        output_format = OutputFormat(fmt)
    except ValueError:
        output_format = OutputFormat.epub

    format_set = {output_format}
    if OutputFormat.epub in format_set or (format_set & ctx.binder.depends_on_epub):
        format_set.discard(OutputFormat.epub)
        formats = [OutputFormat.epub] + list(format_set)
    else:
        formats = list(format_set)

    artifacts = {}
    for f in formats:
        artifact = ctx.binder.make_artifact(
            novel.id,
            novel.title,
            format=f,
            user_id=user.id,
            epub=artifacts.get(OutputFormat.epub),
        )
        if artifact.is_available:
            artifacts[f] = artifact

    if output_format not in artifacts:
        return {"error": f"Failed to generate {output_format} artifact"}

    artifact = artifacts[output_format]
    file_path = ctx.files.resolve(artifact.output_file)
    delivery = get_file_delivery(file_path, max_size_mb)

    result = {
        "title": novel.title,
        "chapters": len(chapters),
        "format": str(output_format),
        "file_size": artifact.file_size,
    }
    if isinstance(delivery, str):
        result["url"] = delivery
    else:
        result["discord_file"] = delivery
    return result


def _run_search_sync(query: str, source_filter: Optional[str], limit: int) -> list:
    from ..commands.search.helper import perform_search

    ctx.setup()
    ctx.sources.ensure_load()

    sources = ctx.sources.list(
        source_filter,
        can_search=True,
        include_rejected=False,
    )
    if not sources:
        return []

    results = perform_search(
        query=query,
        sources=sources,
        concurrency=15,
        limit=limit,
        timeout=30,
    )
    return [
        {
            "title": r.title,
            "novels": [{"url": n.url, "info": n.info} for n in r.novels],
        }
        for r in results
    ]


def _get_job_status_sync(job_id: Optional[str]) -> dict:
    ctx.setup()
    user = ctx.users.get_admin()
    user_id = user.id

    if job_id:
        job = ctx.jobs.get(job_id)
        return {
            "single": True,
            "job": {
                "id": job.id,
                "title": job.job_title,
                "status": job.status.name,
                "status_emoji": STATUS_EMOJI.get(job.status, "❓"),
                "progress": job.progress,
                "done": job.done,
                "total": job.total,
                "failed": job.failed,
                "error": job.error,
            },
        }

    paginated = ctx.jobs.list(user_id=user_id, limit=10)
    return {
        "single": False,
        "jobs": [
            {
                "id": job.id,
                "title": job.job_title,
                "status": job.status.name,
                "status_emoji": STATUS_EMOJI.get(job.status, "❓"),
                "progress": job.progress,
                "done": job.done,
                "total": job.total,
            }
            for job in paginated.items
        ],
    }


class LightnovelBot(commands.Bot):
    def __init__(self, guild_id: Optional[int] = None):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.guild_id = guild_id

    async def setup_hook(self):
        @self.tree.command(name="crawl", description="Crawl a novel from a URL")
        @app_commands.describe(
            url="Novel page URL",
            range="Chapter range: all, first N, last N",
            format="Output format (epub, pdf, mobi, etc.)",
        )
        async def crawl_cmd(
            interaction: discord.Interaction,
            url: str,
            range: str = "all",
            format: str = "epub",
        ):
            await interaction.response.defer(ephemeral=False)

            max_size_mb = float(os.getenv("DISCORD_MAX_FILE_SIZE_MB", "25"))
            try:
                result = await asyncio.to_thread(_run_crawl_sync, url, range, format, max_size_mb)
            except Exception as e:
                logger.error("Crawl failed", exc_info=True)
                await interaction.followup.send(f"❌ Crawl failed: {e}")
                return

            if "error" in result:
                await interaction.followup.send(f"❌ {result['error']}")
                return

            from ..utils.file_tools import format_size

            size_str = format_size(result["file_size"] or 0)
            msg = (
                f"**{result['title']}**\n"
                f"📖 {result['chapters']} chapters · {result['format']} ({size_str})"
            )

            if "discord_file" in result:
                await interaction.followup.send(msg, file=result["discord_file"])
            elif "url" in result:
                await interaction.followup.send(f"{msg}\n📥 Download: {result['url']}")
            else:
                await interaction.followup.send(msg)

        @self.tree.command(name="search", description="Search for novels across sources")
        @app_commands.describe(
            query="Search query",
            source="Filter by source name",
            limit="Maximum number of results",
        )
        async def search_cmd(
            interaction: discord.Interaction,
            query: str,
            source: Optional[str] = None,
            limit: int = 10,
        ):
            await interaction.response.defer(ephemeral=False)

            try:
                results = await asyncio.to_thread(_run_search_sync, query, source, limit)
            except Exception as e:
                logger.error("Search failed", exc_info=True)
                await interaction.followup.send(f"❌ Search failed: {e}")
                return

            if not results:
                await interaction.followup.send(f'No results found for "{query}"')
                return

            embed = discord.Embed(
                title=f'Search results for "{query}"',
                color=discord.Color.blue(),
            )
            for r in results[:10]:
                novels_text = "\n".join(
                    f"• [{n['url']}]({n['url']})" + (f"\n  _{n['info']}_" if n.get("info") else "")
                    for n in r["novels"][:3]
                )
                embed.add_field(
                    name=f"📚 {r['title']} ({len(r['novels'])} results)",
                    value=novels_text or "No details",
                    inline=False,
                )

            await interaction.followup.send(embed=embed)

        @self.tree.command(name="status", description="Check job status")
        @app_commands.describe(
            job_id="Job ID to check (leave empty for recent jobs)",
        )
        async def status_cmd(
            interaction: discord.Interaction,
            job_id: Optional[str] = None,
        ):
            await interaction.response.defer(ephemeral=False)

            try:
                result = await asyncio.to_thread(_get_job_status_sync, job_id)
            except Exception as e:
                logger.error("Status check failed", exc_info=True)
                await interaction.followup.send(f"❌ {e}")
                return

            if result["single"]:
                job = result["job"]
                embed = discord.Embed(
                    title=f"{job['status_emoji']} Job {job['id'][:8]}",
                    description=job["title"],
                    color=(
                        discord.Color.green()
                        if job["status"] == "SUCCESS"
                        else discord.Color.orange()
                    ),
                )
                embed.add_field(name="Status", value=job["status"], inline=True)
                embed.add_field(
                    name="Progress",
                    value=f"{job['progress']}% ({job['done']}/{job['total']})",
                    inline=True,
                )
                if job.get("failed"):
                    embed.add_field(name="Failed", value=str(job["failed"]), inline=True)
                if job.get("error"):
                    embed.add_field(name="Error", value=job["error"], inline=False)
                await interaction.followup.send(embed=embed)
            else:
                jobs = result["jobs"]
                if not jobs:
                    await interaction.followup.send("No jobs found.")
                    return

                embed = discord.Embed(
                    title="Recent Jobs",
                    color=discord.Color.blue(),
                )
                for job in jobs:
                    embed.add_field(
                        name=f"{job['status_emoji']} {job['id'][:8]} — {job['status']}",
                        value=(
                            f"{job['title']}\n"
                            f"Progress: {job['progress']}% ({job['done']}/{job['total']})"
                        ),
                        inline=False,
                    )
                await interaction.followup.send(embed=embed)

        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Synced commands to guild {self.guild_id}")
        else:
            await self.tree.sync()
            logger.info("Synced commands globally")

    async def on_ready(self):
        user_id = self.user.id if self.user else "unknown"
        logger.info(f"Bot connected as {self.user} (ID: {user_id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for novel requests",
            )
        )
