from typing import Dict, List

from rich import print
import typer

from ...context import ctx


def recover_empty_chapters(
    apply: bool = typer.Option(False, "--apply", help="Clear the flag instead of reporting."),
    include_tried: bool = typer.Option(
        False,
        "--include-tried",
        help="Also reopen chapters already given up on after repeated empty downloads.",
    ),
):
    """Find chapters stored with an empty body and let them be fetched again.

    The background scrubber does this on its own for chapters stored before empty bodies
    were detected at all. This command reports what it would touch before touching it,
    and can reach the ones the scrubber leaves alone: chapters given up on after their
    retries ran out, which are worth another attempt once the source itself is fixed.
    """
    ctx.setup(sync_remote_index=False)

    found = list(ctx.chapters.find_stored_empty(untried_only=not include_tried))
    if not found:
        print("[green]No chapter is stored with an empty body.[/green]")
        return

    by_novel: Dict[str, List[int]] = {}
    for item in found:
        by_novel.setdefault(item.novel_id, []).append(item.serial)
    print(f"[yellow]{len(found)}[/yellow] empty across [yellow]{len(by_novel)}[/yellow] novel(s)")
    for novel_id, serials in list(by_novel.items())[:10]:
        title = ctx.novels.get(novel_id).title
        print(f"  {title}: {len(serials)} (first: {sorted(serials)[:5]})")

    if not apply:
        print("\nRe-run with [cyan]--apply[/cyan] to let these be fetched again.")
        return

    total = ctx.chapters.reopen_empty([item.id for item in found], reset_attempts=True)
    print(f"[green]Cleared {total} chapter(s); the next fetch will download them.[/green]")
