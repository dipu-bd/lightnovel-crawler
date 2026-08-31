"""Serving a host from a declarative spec instead of a Python crawler.

The interpreter lives in its own package and knows nothing about this application, so this
module is the whole seam between them: it turns a spec into something `Crawler`-shaped, and it
maps the interpreter's models onto this application's.

The import is lazy and optional on purpose. Until `lncrawl-sourcelib` is published, a checkout
of this repository has no way to resolve it, and lncrawl must keep working exactly as it does
today when it is absent. So a missing interpreter means no spec tier, not a broken application.

The adapter below should stay a copy rather than a translation. If it starts *fixing up* values
instead of moving them, the two sets of models have diverged and replacing this application's
core stops being a deletion.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Type

from ...core import Crawler
from ...core.models import Chapter, Novel, SearchResult, Volume
from ...core.tiers import SPEC

logger = logging.getLogger(__name__)

__all__ = ["available", "load_specs", "to_novel", "unreadable"]


def available() -> bool:
    """Whether the interpreter is installed."""
    try:
        import sourcelib  # type: ignore[import-not-found] # noqa: F401
    except ImportError:
        return False
    return True


def _requirement_hint() -> str:
    return (
        "the spec tier needs lncrawl-sourcelib. For local development, link a sibling "
        "checkout with `make link-sourcelib`"
    )


def to_novel(source: Any, novel: Novel) -> None:
    """Copy an interpreter Novel onto this application's, in place.

    One field genuinely differs: the interpreter carries `authors` as a list, because that is
    what a two-author site has and what `all: true` yields. This application stores one
    comma-joined string, so the join happens here and nowhere else. When the application takes
    the list, this line goes and the adapter is a pure copy.
    """
    novel.title = source.title or novel.title
    novel.cover_url = source.cover_url or ""
    novel.author = ", ".join(a for a in source.authors if a)
    novel.synopsis = source.synopsis or ""
    novel.tags = list(source.tags or [])
    if source.language:
        novel.language = source.language
    novel.is_manga = source.is_manga
    novel.is_mtl = source.is_mtl

    novel.volumes = [Volume(id=v.id, title=v.title) for v in source.volumes]
    novel.chapters = [
        Chapter(
            id=c.id,
            url=c.url,
            title=c.title,
            volume=c.volume,
            **_spreadable(c.extras),
        )
        for c in source.chapters
    ]


#: The keyword arguments this module passes by name. An extra of the same name arrives as a second
#: value for one parameter, which is a TypeError rather than an override — a spec that names a toc
#: field `id` took the whole source down with
#: `Chapter() got multiple values for keyword argument 'id'`.
_SPREAD_RESERVED = ("id", "url", "title", "volume", "info")


def _spreadable(extras: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """*extras* minus the names this module already passes.

    Dropping rather than renaming: the field is still on the row the interpreter produced, and a
    silent rename would put a chapter's `id` somewhere no reader would look for it.
    """
    return {k: v for k, v in (extras or {}).items() if k not in _SPREAD_RESERVED}


def _search_results(rows: Iterable[Any]) -> List[SearchResult]:
    return [
        SearchResult(title=r.title, url=r.url, info=r.info, **_spreadable(r.extras)) for r in rows
    ]


def build_crawler(spec: Any, root: Path, host: str, path: Path) -> Type[Crawler]:
    """A Crawler subclass that interprets *spec*.

    Every instance builds its own interpreter, because the interpreter holds per-crawl state and
    a crawler class is shared by every crawl of its host.
    """
    from sourcelib import Interpreter  # type: ignore[import-not-found]
    from sourcelib.net.scraper import ScraperFetcher  # type: ignore[import-not-found]

    can = _capabilities(spec)

    class SpecCrawler(Crawler):
        base_url = [str(spec.base_url)]
        tier = SPEC

        # Never left empty: the index derives a language from the file path when a crawler
        # declares none, which for a spec would yield its filename. Detection at crawl time
        # overrides this anyway (RFC-0001 section 3.2).
        language = spec.language or "en"
        has_mtl = spec.has_mtl
        has_manga = spec.has_manga
        request_rate_limit = spec.rate_limit
        chapters_per_volume = spec.chapters_per_volume
        is_disabled = bool(spec.disabled)
        disable_reason = spec.disabled or ""

        # Asked of the interpreter rather than recomputed here. This read `spec.search is not
        # None`, which ignores both an explicit `can_search: false` and a search supplied by a
        # hook, so a source turned off on purpose still advertised search.
        can_search = can["can_search"]
        can_login = can["can_login"]

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self._interpreter: Optional[Any] = None

        @property
        def interpreter(self) -> Any:
            if self._interpreter is None:
                self._interpreter = Interpreter.load(
                    spec, ScraperFetcher(session=self.scraper), root=root
                )
            return self._interpreter

        def search(self, query: str) -> Iterable[SearchResult]:
            return _search_results(self.interpreter.search(query))

        def read_novel(self, novel: Novel) -> None:
            to_novel(self.interpreter.read_novel(str(novel.url)), novel)

        def download_chapter(self, chapter: Chapter) -> None:
            # The interpreter needs the novel only for its address, so a bare stand-in is
            # enough. Reading the novel again here would fetch its page once per chapter.
            source = self.interpreter.download_chapter(
                _as_source_novel(self.novel_url or self.base_url[0]),
                _as_source_chapter(chapter),
            )
            chapter.body = source.body
            chapter.images = dict(source.images or {})

    SpecCrawler.__name__ = f"Spec_{host.replace('.', '_').replace('-', '_')}"
    SpecCrawler.__qualname__ = SpecCrawler.__name__

    setattr(SpecCrawler, "__id__", hashlib.md5(f"spec:{host}".encode()).hexdigest())
    setattr(SpecCrawler, "__file__", str(path))
    setattr(SpecCrawler, "version", _content_version(path))
    setattr(SpecCrawler, "updated_at", _mtime(path))
    return SpecCrawler


def _capabilities(spec: Any) -> Dict[str, bool]:
    """What a resolved spec can do, as the interpreter derives it.

    `bound` is the set of hook points actually bound. A spec naming a whole hook file binds
    whatever that file defines, which only the hook loader knows, so a declared mapping is all
    this can offer and a bare path is treated as binding nothing here.
    """
    from sourcelib.spec.validate import capabilities  # type: ignore[import-not-found]

    declared = spec.hooks if isinstance(spec.hooks, dict) else {}
    return capabilities(spec, set(declared))


def _content_version(path: Path) -> int:
    try:
        digest = hashlib.md5(path.read_bytes()).hexdigest()
    except OSError:  # pragma: no cover - the registry just read this file
        return 0
    return int(digest[:8], 16)


def _mtime(path: Path) -> int:
    try:
        return int(path.stat().st_mtime)
    except OSError:  # pragma: no cover - the registry just read this file
        return 0


def _as_source_novel(url: str) -> Any:
    from sourcelib import Novel as SourceNovel  # type: ignore[import-not-found]

    return SourceNovel(url=str(url))


def _as_source_chapter(chapter: Chapter) -> Any:
    from sourcelib import Chapter as SourceChapter  # type: ignore[import-not-found]

    known = ("id", "url", "title", "volume", "body", "images", "success")
    return SourceChapter(
        id=int(chapter.id),
        url=str(chapter.url or ""),
        title=str(chapter.title or ""),
        volume=chapter.volume,
        extras={k: v for k, v in chapter.items() if k not in known and not k.startswith("__")},
    )


#: How many specs the last load could not read. Reported with the tier tally, because a spec that
#: fails to load leaves its host on the legacy crawler and is otherwise indistinguishable from a
#: host that never had a spec — which is how an interpreter one minor version too old hid 36 of
#: them behind a per-file warning nobody reads.
unreadable = 0


def load_specs(root: Optional[Path]) -> Dict[str, Type[Crawler]]:
    """Every servable spec under *root*, as host -> Crawler subclass.

    Returns nothing at all when the interpreter is absent or the directory does not exist, so a
    checkout without either behaves exactly as it does today.
    """
    global unreadable
    unreadable = 0
    if root is None or not Path(root).is_dir():
        return {}
    if not available():
        logger.info(_requirement_hint())
        return {}

    from sourcelib import Registry  # type: ignore[import-not-found]

    registry = Registry.load(Path(root))
    for path, reason in registry.problems:
        logger.warning(f"\\[{path}] spec could not be read: {reason}")
    unreadable = len(registry.problems)

    built: Dict[str, Type[Crawler]] = {}
    for entry in registry.served:
        try:
            built[entry.host] = build_crawler(entry.spec, Path(root), entry.host, entry.path)
        except Exception as error:
            logger.warning(f"\\[{entry.path}] spec could not be loaded: {error!r}")
            unreadable += 1
    return built
