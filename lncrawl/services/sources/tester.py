import hashlib
import types
from typing import Any, Callable, List, Type

from scraper import extract_base

from lncrawl.context import ctx
from lncrawl.core import Chapter, Crawler, Novel, PageSoup
from lncrawl.services.sources.helper import extract_crawlers
from lncrawl.utils.log_sink import LogSink


def parse_content(host: str, content: str):
    mod_name = hashlib.md5(content.encode()).hexdigest()
    module = types.ModuleType(mod_name)
    module.__file__ = f"{mod_name}_test.py"
    exec(compile(content, module.__file__, "exec"), module.__dict__)
    for constructor in extract_crawlers(module):
        for url in constructor.base_url:
            if host == extract_base(url):
                return constructor
    raise RuntimeError(f"No crawler found for {host}")


def run_crawler_test(
    url: str,
    content: str,
    emit: Callable[[str], Any],
) -> None:
    _W = 50

    def step(msg: str) -> None:
        emit(f"\n>>> {msg}")

    def meta(key: str, value: str) -> None:
        emit(f"    {key}: {value}")

    def section(title: str) -> None:
        prefix = f"─── {title} "
        suffix = "─" * max(1, _W - len(prefix))
        emit("\n" + prefix + suffix)

    def divider():
        emit("─" * _W)

    def show_novel(novel: Novel):
        meta("title", novel.title)
        meta("cover", novel.cover_url)
        meta("author", novel.author)
        meta("language", novel.language or "")
        meta("manga", str(novel.is_manga))
        meta("MTL", str(novel.is_mtl))
        meta("tags", ", ".join(novel.tags))
        meta("extras", str(novel.get_extras()))
        meta("volumes", f"{len(novel.volumes)}")
        meta("chapters", f"{len(novel.chapters)}")

        section("Novel Data")
        emit(novel.to_yaml(indent=4, sort_keys=False))
        divider()

    def show_chapter(chapter: Chapter):
        meta("title", repr(chapter.title))
        meta("volume", repr(chapter.volume))
        meta("images", repr(chapter.images))
        meta("extras", str(chapter.get_extras()))

        section(f"Chapter {chapter.id}")
        emit(PageSoup.create(chapter.body).find("body").prettify(True))
        emit("─" * 50)

    def show_crawler_cls(crawler_cls: Type[Crawler]):
        meta("class", repr(crawler_cls))
        meta("supported urls", ", ".join(crawler_cls.base_url))
        meta("login", str(crawler_cls.can_login))
        meta("search", str(crawler_cls.can_search))
        meta("language", str(crawler_cls.language))
        meta("has_mtl", str(crawler_cls.has_mtl))
        meta("has_manga", str(crawler_cls.has_manga))

    step("Parsing content")
    origin = extract_base(url)
    constructor = parse_content(origin, content)
    show_crawler_cls(constructor)

    # Pipe the crawler's internal log sink to our stdout emitter.
    crawler_log_sink = getattr(constructor, "__logs__", None)
    assert isinstance(crawler_log_sink, LogSink)
    crawler_log_sink.attach(emit)

    step("Initializing crawler")
    crawler = constructor(
        origin=origin,
        scraper=ctx.scraper.open(
            origin,
            rate_limit=constructor.request_rate_limit,
        ),
    )
    crawler.initialize()
    meta("origin", origin)

    step("Reading novel info")
    novel = Novel(url=url)
    meta("url", url)
    crawler.read_novel(novel)
    crawler.format_novel(novel)
    show_novel(novel)

    chapters: List[Chapter] = []
    if novel.chapters:
        chapters.append(novel.chapters[0])
    if len(novel.chapters) > 1:
        chapters.append(novel.chapters[-1])

    for chapter in chapters:
        step(f"Downloading chapter {chapter.id}")
        meta("url", chapter.url)
        crawler.download_chapter(chapter)
        crawler.format_chapter(chapter)
        show_chapter(chapter)
