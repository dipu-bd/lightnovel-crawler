import json
from typing import Optional

import questionary
import typer
import yaml
from rich import print
from rich.console import Console

from ..context import ctx

app = typer.Typer(
    help="View and modify configuration settings.",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def config():
    ctx.setup()


@app.command("view", help="View configuration sections.")
def view_config(
    format: Optional[str] = typer.Option(
        None, "--format", "-f", help="Format to view the configuration"
    ),
):
    data = ctx.config._data.copy()
    data.pop("__deprecated__", None)
    if format == "yaml":
        print(yaml.dump(data, indent=2, sort_keys=True))
    elif format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        for section in sorted(data.keys()):
            print(f"[green]{section}[/green]:")
            for key in sorted(data[section].keys()):
                value = data[section][key]
                value_type = type(value).__name__
                print(f"  [cyan]{key}[/cyan]: [dim]{value_type}[/dim] =", json.dumps(value))
            print()


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
    if not section:
        section = _prompt_section()

    if section not in ctx.config._data:
        print(f'[red]Invalid section: "{section}"[/red]')
        raise typer.Exit(1)

    if not key:
        key = _prompt_key(section)

    if key not in ctx.config._data[section]:
        print(f'[red]Invalid key: "{key}" for section: "{section}"[/red]')
        raise typer.Exit(1)

    value = ctx.config.get(section, key)
    value_type = type(value).__name__
    print(
        f"[green]{section}[/green].[cyan]{key}[/cyan]: [dim]{value_type}[/dim] =",
        value,
    )


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
    if not section:
        section = _prompt_section()

    if section not in ctx.config._data:
        print(f'[red]Invalid section: "{section}"[/red]')
        raise typer.Exit(1)

    if not key:
        key = _prompt_key(section)

    if key not in ctx.config._data[section]:
        print(f'[red]Invalid key: "{key}" for section: "{section}"[/red]')
        raise typer.Exit(1)

    if value is None:
        value = _prompt_value(section, key)

    if value is not None:
        ctx.config.set(section, key, value)
        print(f"[green]✓[/green] Set [green]{section}.{key}[/green] =", value)


def _prompt_section() -> str:
    return questionary.select(
        "Select a section:",
        choices=sorted([k for k in ctx.config._data.keys() if k != "__deprecated__"]),
    ).unsafe_ask()


def _prompt_key(section: str) -> str:
    return questionary.select(
        "Select a key:",
        choices=sorted(ctx.config._data[section].keys()),
    ).unsafe_ask()


def _prompt_value(section: str, key: str) -> str:
    value = ctx.config.get(section, key)
    return questionary.text(
        "Enter value:",
        default=str(value),
    ).unsafe_ask()
