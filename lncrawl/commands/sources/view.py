from datetime import datetime

import typer

from ...context import ctx
from .app import app


@app.command("view", help="Inspect a source.")
def view_one(
    query: str = typer.Argument(
        help="The source name, url, or file path to find exact source.",
    ),
):
    import questionary
    from rich import print
    from rich.text import Text

    # Find unique source
    sources = ctx.sources.list(query, include_rejected=True)
    if not sources:
        print("[red]No source found.[/red]")
        return

    if len(sources) > 5:
        print("[i]Please modify your query to find a unique source![/i]")
        print(f"[red]{len(sources)} sources found.[/red]")
        return

    if len(sources) != 1:
        item = questionary.select(
            "Choose a source",
            choices=[questionary.Choice(item.url, value=(item)) for item in sources],
        ).unsafe_ask()
    else:
        item = sources[0]

    # Display supported urls
    print("[green]:right_arrow: URL:[/green]", end="")
    print(f" [cyan]{item.url}[/cyan]")

    # Display features
    features = []
    if item.has_mtl:
        features.append("Machine Translation")
    if item.has_manga:
        features.append("Manga")
    if item.can_search:
        features.append("Search")
    if item.can_login:
        features.append("Login")
    if features:
        print("[green]:right_arrow: Features:[/green]", end="")
        if len(features) > 1:
            print()
            for feature in features:
                print(f"  - {feature}")
        else:
            print(f" {features[0]}")

    # Display version
    print(
        "[green]:right_arrow: Last Update:[/green]",
        datetime.fromtimestamp(item.version).strftime(r"%Y %b %d %I:%M:%S %p"),
    )

    # Display commit count and contributors
    contribs = ", ".join(item.contributors)
    if contribs:
        if item.total_commits > 0:
            contribs = f"{item.total_commits} commits by {contribs}"
        print("[green]:right_arrow: Contributors:[/green]", contribs)

    # Display source file
    print(
        "[green]:right_arrow: Source file:[/green]",
        Text(str(item.file_path), style="cyan", no_wrap=True),
    )

    # Display download link
    if item.url:
        print(
            "[green]:right_arrow: Download URL:[/green]", Text(item.url, style="cyan", no_wrap=True)
        )
