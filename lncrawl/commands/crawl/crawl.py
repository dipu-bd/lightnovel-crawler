from __future__ import annotations

import logging
from typing import Dict, List, Optional

from rich import print
import typer

from ...context import ctx
from ...enums import OutputFormat
from .app import app

logger = logging.getLogger(__name__)


@app.command(help="Crawl from novel page URL.")
def crawl(
    non_interactive: bool = typer.Option(
        False,
        "--noin",
        help="Disable interactive mode",
    ),
    range_all: Optional[bool] = typer.Option(
        None, "--all", is_flag=True, help="Download all chapters"
    ),
    range_first: Optional[int] = typer.Option(
        None, "--first", min=1, metavar="N", help="Download first few chapters"
    ),
    range_last: Optional[int] = typer.Option(
        None,
        "--last",
        min=1,
        metavar="N",
        help="Download latest few chapters",
    ),
    formats: List[OutputFormat] = typer.Option(
        [],
        "-f",
        "--format",
        show_choices=True,
        help="Output formats",
    ),
    username: Optional[str] = typer.Option(
        None,
        "--user",
        help="Username/Email",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--pass",
        help="Password/Token",
    ),
    url: str = typer.Argument(
        default=None,
        help="Novel details page URL.",
    ),
):
    from rich.console import Console
    from rich.panel import Panel

    from ...dao import Artifact
    from ...exceptions import ServerError
    from ...utils.file_tools import format_size, open_folder
    from .prompts import (
        prompt_format_selection,
        prompt_login_details,
        prompt_open_artifact_folder,
        prompt_range_selection,
        prompt_url,
    )

    console = Console()

    # setup context
    ctx.setup()

    # ensure url
    if not url:
        if non_interactive:
            print("[red]Please enter a novel page URL[/red]")
            return
        url = prompt_url()
    if not url:
        return

    # init crawler
    try:
        crawler = ctx.sources.init_crawler(url)
        can_login = getattr(crawler, "can_login", False)
    except ServerError as e:
        print(f"[red]{e.format(True)}[/red]")
        return

    # get login details
    if can_login:
        if not (username and password):
            if not non_interactive:
                username, password = prompt_login_details()
        if username and password:
            crawler.login(username, password)

    # fetch novel details
    with console.status("Fetching novel details..."):
        user = ctx.users.get_admin()
        novel = ctx.crawler.fetch_novel(user.id, url, crawler=crawler)
    print(
        Panel(
            "\n".join(
                filter(
                    None,
                    [
                        f"[cyan]{novel.url}[/cyan]",
                        f"[yellow][b]{novel.title}[/b][/yellow]",
                        f"[green]{novel.authors}[/green]" if novel.authors else None,
                        f"[i]{novel.volume_count} volumes, {novel.chapter_count} chapters[/i]",
                    ],
                )
            )
        )
    )

    if novel.chapter_count == 0:
        print("[red]No chapters to download[/red]")
        return

    # select chapters to download
    chapters: List[str] = []
    if not non_interactive and all(
        [
            range_all is None,
            range_first is None,
            range_last is None,
        ]
    ):
        chapters = prompt_range_selection(novel)
    else:
        chapters = ctx.chapters.list_ids(
            novel_id=novel.id, descending=bool(range_last), limit=range_last or range_first
        )
    if not chapters:
        print("[red]No chapters to download[/red]")
        return

    # select formats to bind
    if not formats:
        if non_interactive:
            formats = list(OutputFormat)
        else:
            formats = prompt_format_selection()

    # download chapters
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

    # download chapter images
    image_futures = [
        crawler.taskman.submit_task(
            ctx.crawler.fetch_image,
            user.id,
            image_id,
            crawler=crawler,
        )
        for image_id in sorted(set(chapter_image_ids))
    ]
    crawler.taskman.resolve_futures(
        image_futures,
        desc="Images",
        unit=" img",
    )

    # create artifacts
    format_set = set(formats)
    if OutputFormat.epub in format_set or (format_set & ctx.binder.depends_on_epub):
        format_set -= set([OutputFormat.epub])
        formats = [OutputFormat.epub] + list(format_set)
    else:
        formats = list(format_set)

    artifacts: Dict[OutputFormat, Artifact] = {}
    for fmt in formats:
        with console.status(f"Generating {fmt}..."):
            artifact = ctx.binder.make_artifact(
                novel.id,
                novel.title,
                format=fmt,
                user_id=user.id,
                epub=artifacts.get(OutputFormat.epub),
            )
        if artifact.is_available:
            artifacts[fmt] = artifact
            file = ctx.files.resolve(artifact.output_file)
            size = format_size(artifact.file_size or 0)
            print(f"[b]{fmt}[/b] ({size}): [cyan]{file}[/cyan]")
        else:
            print(f"[red]Failed to generate [b]{fmt.value}[/b][/red]")

    if not non_interactive and prompt_open_artifact_folder():
        cover_file = ctx.files.resolve(novel.cover_file)
        open_folder(cover_file.parent / "artifacts")
