import csv
import json
import sys
from typing import Optional

from rich import print
import typer

from ...assets.icons import Icons
from ...context import ctx
from .app import app


@app.command("list", help="List available sources.")
def list_all(
    query: Optional[str] = typer.Option(
        None,
        "-q",
        "--query",
        help="Filter sources by keyword in the URL.",
    ),
    can_search: Optional[bool] = typer.Option(
        None,
        "-s",
        "--can-search",
        help="Show only sources that support novel search.",
    ),
    can_login: Optional[bool] = typer.Option(
        None,
        "-l",
        "--can-login",
        help="Show only sources that support login.",
    ),
    has_mtl: Optional[bool] = typer.Option(
        None,
        "-b",
        "--mtl",
        help="Show only machine-translated sources.",
    ),
    has_manga: Optional[bool] = typer.Option(
        None,
        "-m",
        "--manga",
        help="Show only manga/manhua sources.",
    ),
    include_rejected: bool = typer.Option(
        False,
        "--with-rejected",
        help="Include rejected or disabled sources in the list.",
    ),
    output_type: Optional[str] = typer.Option(
        "table",
        "-o",
        "--output-type",
        help="Output type: table, json, yaml, csv, text. Default: table.",
    ),
):
    """
    Display a list of supported crawler sources.
    Filters can be combined to narrow down the results.
    """
    from rich.table import Table
    from rich.text import Text
    import yaml

    sources = ctx.sources.list(
        query=query,
        include_rejected=include_rejected,
        can_search=can_search,
        can_login=can_login,
        has_mtl=has_mtl,
        has_manga=has_manga,
    )

    if not sources:
        print("[red]No sources found.[/red]")
        return

    if not output_type or output_type == "table":
        table = Table(title="List supported sources")
        table.add_column("#", style="cyan", no_wrap=True, justify="right")
        table.add_column("URL", overflow="fold")
        table.add_column("Search", justify="center")
        table.add_column("Login", justify="center")
        table.add_column("Manga", justify="center")
        table.add_column("MTL", justify="center", min_width=5)
        for i, item in enumerate(sources):
            yes_no = {
                True: Icons.CHECK,
                False: "",
            }
            url = Text(item.url, style="blue")
            if query:
                url.highlight_regex(query, style="yellow")
            table.add_row(
                str(i),
                url,
                yes_no[item.can_search],
                yes_no[item.can_login],
                yes_no[item.has_manga],
                yes_no[item.has_mtl],
            )
        print(table)
    elif output_type in ["json", "yaml", "yml"]:
        data = [
            {
                "url": item.url,
                "version": item.version,
                "file": str(item.file_path),
                "language": str(item.language),
                "features": {
                    "Search": bool(item.can_search),
                    "Login": bool(item.can_login),
                    "Manga": bool(item.has_manga),
                    "MTL": bool(item.has_mtl),
                },
                "disabled": item.disable_reason if item.is_disabled else False,
            }
            for item in sources
        ]
        if output_type in ["yaml", "yml"]:
            print(yaml.safe_dump(data, indent=4, sort_keys=False))
        else:
            print(json.dumps(data, indent=4, sort_keys=False))
    elif output_type == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["#", "URL", "Search", "Login", "Manga", "MTL"])
        for i, item in enumerate(sources):
            writer.writerow(
                [
                    i,
                    item.url,
                    item.can_search,
                    item.can_login,
                    item.has_manga,
                    item.has_mtl,
                ]
            )
    elif output_type == "text":
        for i, item in enumerate(sources):
            features = {
                "Search": item.can_search,
                "Login": item.can_login,
                "Manga": item.has_manga,
                "MTL": item.has_mtl,
            }
            enabled_features = [feature for feature, enabled in features.items() if enabled]
            feature_list = ", ".join(enabled_features)
            if feature_list:
                feature_list = f" [green]({feature_list})[/green]"
            print(f"{i:3}: {item.url:40}\t{feature_list}")
    else:
        print("[red]Invalid output type: {output_type}[/red]")
