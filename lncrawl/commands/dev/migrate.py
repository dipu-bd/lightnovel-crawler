from rich import print
import typer

from ...context import ctx

app = typer.Typer(
    help="DB migrations.",
    no_args_is_help=True,
)


@app.callback()
def migrate():
    ctx.db._ensure_database()


@app.command("add", help="Create a new revision file.")
def app_add(
    disable_auto: bool = typer.Option(
        False,
        "-n",
        "--no-auto",
        is_flag=True,
        help="Disable auto generation",
    ),
    message: str = typer.Argument(
        help="Migration message.",
    ),
):
    from alembic import command

    command.revision(
        config=ctx.db.alembic_config,
        autogenerate=not disable_auto,
        message=message,
    )


@app.command("up", help="Upgrade to a later version.")
def app_upgrade(
    revision: str = typer.Argument(
        default="head",
        help='Revision target. "head" to target the most recent',
    ),
):
    from alembic import command

    command.upgrade(
        config=ctx.db.alembic_config,
        revision=revision,
    )
    app_status()


@app.command("down", help="Downgrade to a former revision.")
def app_downgrade(
    revision: str = typer.Argument(
        default="-1",
        help='Revision target. "base" to target the first revision.',
    ),
):
    from alembic import command

    current = ctx.db.current_revision()
    if not current:
        print("[red]No revisions to downgrade.[/red]")
    else:
        command.downgrade(
            config=ctx.db.alembic_config,
            revision=revision,
        )
    app_status()


@app.command("status", help="Display the current revision.")
def app_status():
    latest = ctx.db.latest_revision()
    current = ctx.db.current_revision()
    print(f"Current: [yellow]{current}[/yellow]", end=" ")
    if latest == current:
        print("(latest)")
    else:
        print(f"(Latest: [yellow]{latest}[/yellow])")
