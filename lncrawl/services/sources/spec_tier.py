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
from typing import Any, Dict, Iterable, List, Optional, Type

from ...core import Crawler
from ...core.models import Chapter, Novel, SearchResult, Volume
from ...core.tiers import SPEC

logger = logging.getLogger(__name__)

__all__ = ["available", "load_specs", "to_novel"]


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
            **(c.extras or {}),
        )
        for c in source.chapters
    ]


def _search_results(rows: Iterable[Any]) -> List[SearchResult]:
    return [SearchResult(title=r.title, url=r.url, info=r.info, **(r.extras or {})) for r in rows]


def build_crawler(spec: Any, root: Path, host: str, path: Path) -> Type[Crawler]:
    """A Crawler subclass that interprets *spec*.

    Every instance builds its own interpreter, because the interpreter holds per-crawl state and
    a crawler class is shared by every crawl of its host.
    """
    from sourcelib.http import ScraperFetcher  # type: ignore[import-not-found]
    from sourcelib.runtime import Interpreter  # type: ignore[import-not-found]

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

        # Derived rather than declared, so a flag cannot drift from what resolves.
        can_search = spec.search is not None
        can_login = "login" in (spec.hooks if isinstance(spec.hooks, dict) else {})

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

    # The registry expects what `extract_crawlers` sets on an imported .py crawler. A spec is
    # not imported, so they are set here rather than discovered.
    setattr(SpecCrawler, "__id__", hashlib.md5(f"spec:{host}".encode()).hexdigest())
    setattr(SpecCrawler, "__file__", str(path))
    # An integer, because the index casts it. A content digest arrives with the manifest, and
    # the value stamped on stored content is already normalised to a string in core/tiers.py.
    setattr(SpecCrawler, "version", _mtime(path))
    return SpecCrawler


def _mtime(path: Path) -> int:
    try:
        return int(path.stat().st_mtime)
    except OSError:  # pragma: no cover - the registry just read this file
        return 0


def _as_source_novel(url: str) -> Any:
    from sourcelib.models import Novel as SourceNovel  # type: ignore[import-not-found]

    return SourceNovel(url=str(url))


def _as_source_chapter(chapter: Chapter) -> Any:
    from sourcelib.models import Chapter as SourceChapter  # type: ignore[import-not-found]

    known = ("id", "url", "title", "volume", "body", "images", "success")
    return SourceChapter(
        id=int(chapter.id),
        url=str(chapter.url or ""),
        title=str(chapter.title or ""),
        volume=chapter.volume,
        extras={k: v for k, v in chapter.items() if k not in known and not k.startswith("__")},
    )


def load_specs(root: Optional[Path]) -> Dict[str, Type[Crawler]]:
    """Every servable spec under *root*, as host -> Crawler subclass.

    Returns nothing at all when the interpreter is absent or the directory does not exist, so a
    checkout without either behaves exactly as it does today.
    """
    if root is None or not Path(root).is_dir():
        return {}
    if not available():
        logger.info(_requirement_hint())
        return {}

    from sourcelib.registry import Registry  # type: ignore[import-not-found]

    registry = Registry.load(Path(root))
    for path, reason in registry.problems:
        logger.warning(f"\\[{path}] spec could not be read: {reason}")

    built: Dict[str, Type[Crawler]] = {}
    for entry in registry.served:
        try:
            built[entry.host] = build_crawler(entry.spec, Path(root), entry.host, entry.path)
        except Exception as error:
            logger.warning(f"\\[{entry.path}] spec could not be loaded: {error!r}")
    return built
