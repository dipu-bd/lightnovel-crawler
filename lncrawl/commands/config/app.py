import typer

app = typer.Typer(
    help="View and modify configuration settings.",
    no_args_is_help=True,
)


@app.callback()
def config():
    from ...context import ctx

    ctx.setup()
