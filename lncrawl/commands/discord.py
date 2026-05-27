from __future__ import annotations

import os

import typer

from ..context import ctx

app = typer.Typer()


@app.command(help="Start Discord bot.")
def discord():
    from ..discord_bot import start_bot

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN environment variable is not set.")
        raise typer.Exit(1)

    guild_id_str = os.getenv("DISCORD_GUILD_ID")
    guild_id = None
    if guild_id_str:
        try:
            guild_id = int(guild_id_str)
        except ValueError:
            print("Error: DISCORD_GUILD_ID must be an integer.")
            raise typer.Exit(1)

    ctx.setup()

    try:
        start_bot(token, guild_id=guild_id)
    finally:
        ctx.destroy()
