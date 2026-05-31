from typing import Optional

from rich import print
import typer

from ...context import ctx
from .app import app


@app.command("get", help="View configuration values.")
def get_config(
    section: Optional[str] = typer.Argument(
        None,
        help="Section to get the value from",
    ),
    key: Optional[str] = typer.Argument(
        None,
        help="Key to get the value for",
    ),
):
    """
    Get configuration value by path name.

    Examples:
        lncrawl config get app openai_api_key
        lncrawl config get mail smtp_port -f yaml
        lncrawl config get crawler runner_concurrency
    """
    from .prompts import prompt_key, prompt_section

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

    value = ctx.config.get(section, key)
    value_type = type(value).__name__
    print(
        f"[green]{section}[/green].[cyan]{key}[/cyan]: [dim]{value_type}[/dim] =",
        value,
    )
