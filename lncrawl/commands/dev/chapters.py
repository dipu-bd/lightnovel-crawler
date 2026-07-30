from typing import List, Tuple

from rich import print
import sqlmodel as sq
import typer

from ...context import ctx
from ...dao import Chapter

# An empty body compresses to a handful of bytes, so only files this small are worth
# opening — but emptiness is decided on the decoded text, never on the size. The bound is
# generous because reading a few extra tiny files costs nothing and missing one does not.
CANDIDATE_BYTES = 512


def _is_empty(chapter: Chapter) -> bool:
    file = ctx.files.resolve(chapter.content_file)
    try:
        if file.stat().st_size > CANDIDATE_BYTES:
            return False
        return not ctx.files.load_text(chapter.content_file).strip()
    except FileNotFoundError:
        return False
    except Exception:
        # Unreadable is not the same as empty, and re-fetching over a file we simply
        # failed to decode would discard content that may be perfectly good.
        return False


def recover_empty_chapters(
    apply: bool = typer.Option(False, "--apply", help="Clear the flag instead of reporting."),
):
    """Find chapters stored with an empty body and let them be fetched again.

    A chapter that was saved empty is marked done over a file with nothing in it, and the
    refetch gate skips anything already marked done — so without this pass the fix for
    empty chapters changes nothing for a library that already has them.
    """
    ctx.setup(sync_remote_index=False)

    with ctx.db.session() as sess:
        done = list(sess.exec(sq.select(Chapter).where(sq.col(Chapter.is_done).is_(True))))

    empty: List[Tuple[str, int]] = []
    for chapter in done:
        if _is_empty(chapter):
            empty.append((chapter.novel_id, chapter.serial))

    print(f"Checked [cyan]{len(done)}[/cyan] chapters marked done")
    if not empty:
        print("[green]No chapter is stored with an empty body.[/green]")
        return

    by_novel: dict = {}
    for novel_id, serial in empty:
        by_novel.setdefault(novel_id, []).append(serial)
    print(f"[yellow]{len(empty)}[/yellow] empty across [yellow]{len(by_novel)}[/yellow] novel(s)")
    for novel_id, serials in list(by_novel.items())[:10]:
        title = ctx.novels.get(novel_id).title
        print(f"  {title}: {len(serials)} (first: {sorted(serials)[:5]})")

    if not apply:
        print("\nRe-run with [cyan]--apply[/cyan] to let these be fetched again.")
        return

    ids = {(novel_id, serial) for novel_id, serial in empty}
    with ctx.db.session() as sess:
        for chapter in sess.exec(sq.select(Chapter).where(sq.col(Chapter.is_done).is_(True))):
            if (chapter.novel_id, chapter.serial) in ids:
                chapter.is_done = False
                extra = dict(**chapter.extra)
                extra.pop("empty_attempts", None)
                chapter.extra = extra
                sess.add(chapter)
        sess.commit()
    print(f"[green]Cleared {len(empty)} chapter(s); the next fetch will download them.[/green]")
