from typing import Optional

from rich import print
import typer

from ...context import ctx
from .app import app


@app.command("set", help="Set a configuration value.")
def set_config(
    section: Optional[str] = typer.Argument(
        None,
        help="Section to set the value in",
    ),
    key: Optional[str] = typer.Argument(
        None,
        help="Key to set the value for",
    ),
    value: Optional[str] = typer.Argument(
        None,
        help="Value to set",
    ),
):
    """
    Set a configuration value.

    Examples:
        lncrawl config set server base_url "https://example.com"
        lncrawl config set crawler runner_concurrency "10"
        lncrawl config set mail smtp_port "587"
    """
    from .prompts import prompt_key, prompt_section, prompt_value

    if not section:
        section = prompt_section()

    if section not in ctx.config._data:
        print(f'[red]Invalid section: "{section}"[/red]')
        raise typer.Exit(1)

    if not key:
        key = prompt_key(section)

    if key not in ctx.config._data[section]:
        print(f'[red]Invalid key: "{key}" for section: "{section}"[/red]')
        raise typer.Exit(1)

    if value is None:
        value = prompt_value(section, key)

    if value is not None:
        ctx.config.set(section, key, value)
        print(f"[green]✓[/green] Set [green]{section}.{key}[/green] =", value)
