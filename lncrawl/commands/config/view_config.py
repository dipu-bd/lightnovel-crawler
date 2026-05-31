from typing import Optional

from rich import print
import typer

from ...context import ctx
from .app import app


@app.command("view", help="View configuration sections.")
def view_config(
    format: Optional[str] = typer.Option(
        None, "--format", "-f", help="Format to view the configuration"
    ),
):
    data = ctx.config._data.copy()
    data.pop("__deprecated__", None)
    if format == "yaml":
        import yaml

        print(yaml.dump(data, indent=2, sort_keys=True))
    elif format == "json":
        import json

        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        import json

        for section in sorted(data.keys()):
            print(f"[green]{section}[/green]:")
            for key in sorted(data[section].keys()):
                value = data[section][key]
                value_type = type(value).__name__
                print(f"  [cyan]{key}[/cyan]: [dim]{value_type}[/dim] =", json.dumps(value))
            print()
