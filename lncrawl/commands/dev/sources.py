from pathlib import Path
from typing import Dict, List, Tuple, Type

from rich import print
from rich.markup import escape
import typer

from ...context import ctx
from ...core import Crawler
from ...core.legacy import LegacyCrawler
from ...services.sources.helper import import_crawlers, load_source

CRAWLER_SURFACE: Tuple[str, ...] = (
    "absolute_url",
    "check_response",
    "cleaner",
    "close",
    "download_chapter",
    "initialize",
    "read_novel",
    "scraper",
    "taskman",
)

LEGACY_SURFACE: Tuple[str, ...] = (
    "cookies",
    "download_file",
    "executor",
    "get_json",
    "get_response",
    "get_soup",
    "headers",
    "make_soup",
    "post_json",
    "post_response",
    "post_soup",
    "render_soup",
    "submit_form",
    "submit_task",
)


def _source_files() -> List[Path]:
    files: List[Path] = []
    for root in [ctx.config.crawler.local_sources, ctx.config.crawler.user_sources]:
        if root.is_dir():
            files.extend(sorted(root.glob("**/*.py")))
    return files


def _label(crawler: Type[Crawler]) -> str:
    file = Path(str(getattr(crawler, "__file__", "?")))
    return f"{file.name}:{crawler.__name__}"


def _check_surface(crawler: Type[Crawler]) -> List[str]:
    try:
        instance = crawler()
    except Exception as e:
        return [f"{_label(crawler)}: failed to construct: {e!r}"]

    expected = CRAWLER_SURFACE
    if isinstance(instance, LegacyCrawler):
        expected += LEGACY_SURFACE
    missing = [attr for attr in expected if not hasattr(instance, attr)]

    try:
        instance.close()
    except Exception as e:
        return [f"{_label(crawler)}: failed to close: {e!r}"]

    if missing:
        return [f"{_label(crawler)}: missing {', '.join(missing)}"]
    return []


def check_sources():
    failures: List[str] = []
    found: Dict[str, Type[Crawler]] = {}

    files = _source_files()
    for file in files:
        try:
            for crawler in import_crawlers(file, strict=True):
                found[getattr(crawler, "__id__")] = crawler
        except Exception as e:
            failures.append(f"{file.name}: failed to load: {e!r}")

    for crawler in found.values():
        failures.extend(_check_surface(crawler))

    index = load_source(ctx.config.crawler.local_index_file)
    vanished = [info for cid, info in index.crawlers.items() if cid not in found]
    for info in sorted(vanished, key=lambda i: i.file_path):
        failures.append(f"{info.file_path}: indexed crawler did not load")

    print(f"Scanned [cyan]{len(files)}[/cyan] files")
    print(
        f"Loaded [cyan]{len(found)}[/cyan] crawlers, index has [cyan]{len(index.crawlers)}[/cyan]"
    )

    unindexed = len(found) - (len(index.crawlers) - len(vanished))
    if unindexed:
        print(f"[yellow]{unindexed} crawler(s) are not in the local index[/yellow]")

    if failures:
        print(f"\n[red]{len(failures)} problem(s):[/red]")
        for line in failures:
            print(f"  [red]*[/red] {escape(line)}")
        raise typer.Exit(code=1)

    print("[green]Every source loads with the expected surface.[/green]")
