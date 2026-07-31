from __future__ import annotations

from abc import ABC, abstractmethod
import hashlib
import math
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Union

from pydantic.networks import HttpUrl
from scraper import extract_base

from ..context import ctx
from ..exceptions import LNException
from ..utils.file_tools import atomic_write
from ..utils.text_tools import format_title, normalize
from .models import Chapter, Novel, SearchResult, Volume

if TYPE_CHECKING:
    from requests import Response
    from scraper import Diagnosis, Scraper


class Crawler(ABC):
    base_url: Union[str, List[str]]

    language = ""
    has_mtl = False
    has_manga = False

    can_login = False
    can_search = False

    request_rate_limit: float = 3.0

    chapters_per_volume = 100
    auto_generate_cover = True

    is_disabled = False
    disable_reason = ""
    version = 0

    @classmethod
    def max_jobs(cls) -> int:
        """Jobs allowed to run against this source at once.

        A fairness bound rather than a throughput one. Measured, throughput keeps
        rising as this grows — a job is far more than its requests, and only the HTTP
        is capped by the scraper's per-address gate, so parsing, cleaning and storing
        overlap freely. What the cap protects is every *other* domain, because one
        source is otherwise free to occupy the whole runner pool.
        """
        if not cls.request_rate_limit:
            return 1
        rate = math.ceil(cls.request_rate_limit)
        return max(1, min(rate, ctx.config.crawler.runner_concurrency))

    @classmethod
    def max_workers(cls) -> int:
        """Threads this crawler's task manager runs.

        One more than the scraper's per-address gate admits, which is not arbitrary:
        measured against a live source, throughput rises to gate+1 and is flat above
        it. The extra thread parses and stores a finished chapter while the others
        hold the permits, so the gate stays fed instead of idling through every parse.

        Deliberately not derived from `request_rate_limit`, which is an interval and
        says nothing about how many threads can be busy at once. Reading it as both is
        what left ten sources single-threaded for declaring no rate limit.
        """
        return max(1, ctx.config.crawler.max_sessions_per_exit) + 1

    @classmethod
    def max_concurrency(cls) -> int:
        """Deprecated alias for `max_workers`.

        Kept because sources are downloaded to disk at runtime, so a user's copy may
        still call it; removing it would make that source fail rather than age.
        """
        return cls.max_workers()

    # ------------------------------------------------------------------------- #
    # Constructor & Destructors
    # ------------------------------------------------------------------------- #
    def __init__(
        self,
        parser: Optional[str] = None,
        origin: Optional[str] = None,
        *,
        scraper: Optional["Scraper"] = None,
    ) -> None:
        """
        Creates a standalone Crawler instance.

        Args:
        - origin (str): The origin URL of the source.
        - parser (Optional[str], optional): Desirable features of the parser. This can be the name of a specific parser
            ("lxml", "lxml-xml", "html.parser", or "html5lib") or it may be the type of markup to be used ("html", "html5", "xml").
        - scraper (Optional[Scraper]): The session to crawl with. Supplied by
            `SourceService`; omitted, one is opened here. Either way it shares the
            process-wide state, so the pacing clock, the held address, the identity and
            what has been learned describe the site rather than this object.
        """
        if isinstance(self.base_url, str):
            self.base_url = [self.base_url]
        if not origin or origin not in self.base_url:
            origin = self.base_url[0]

        from .cleaner import TextCleaner
        from .taskman import TaskManager

        self.cleaner = TextCleaner()
        self.taskman = TaskManager(workers=self.max_workers())

        self.scraper = scraper or ctx.scraper.open(
            origin,
            parser=parser,
            rate_limit=self.request_rate_limit,
        )
        # Attached here rather than passed to `open`, because the session is often
        # opened by `SourceService` and handed in already built.
        self.scraper.check_response = self.check_response

    @property
    def parser(self) -> str:
        """Which parser this crawler's soups are built with.

        A property so a source assigning `self.parser` in `initialize()` reaches the
        session that builds the soup, which is where the choice is read.
        """
        return self.scraper.parser

    @parser.setter
    def parser(self, value: str) -> None:
        self.scraper.parser = value

    def close(self) -> None:
        self.scraper.close()
        self.taskman.close()

    # ------------------------------------------------------------------------- #
    # Methods to implement in crawler
    # ------------------------------------------------------------------------- #

    def initialize(self) -> None:
        pass

    def check_response(self, response: "Response", body: str) -> Optional["Diagnosis"]:
        """Read a response the scraper accepted, and overrule it if it is a refusal.

        Override where a source answers `200` to something it is actually refusing —
        a JSON API returning `{"success": false, "message": ...}`, a page that renders
        an apology at the right status. Nothing can detect that generically: on the
        wire it is indistinguishable from content, and the difference lives in a schema
        only this source knows.

        Worth overriding even though the source could simply raise, because raising
        happens after the retrieval is over. Returning a `Diagnosis` puts the refusal
        *inside* the loop, where the layer is attributed, the address is blamed, and
        the scraper rotates or escalates on its own — so a per-address quota moves to
        the next exit instead of spending every one of them unrecorded.

        Return `None` to accept the response. Called only for responses the scraper
        found nothing wrong with, so there is no need to re-check for a block.
        """
        return None

    def login(self, username_or_email: str, password_or_token: str) -> None:
        pass

    def search(self, query: str) -> Iterable[SearchResult]:
        """Search the source with the given query and yield SearchResult objects"""
        raise NotImplementedError()

    @abstractmethod
    def read_novel(self, novel: Novel) -> None:
        """Scrape the novel details from the source using novel.url"""
        raise NotImplementedError()

    @abstractmethod
    def download_chapter(self, chapter: Chapter) -> None:
        """Download the chapter from the source and set the body of chapter object."""
        raise NotImplementedError()

    # ------------------------------------------------------------------------- #
    # Utility methods that can be overriden
    # ------------------------------------------------------------------------- #

    def absolute_url(self, any_url: Any, page_url: Optional[str] = None) -> str:
        url = str(any_url or "").strip().rstrip("/")
        if not url:
            return url

        scheme = url.split(":")[0]
        if scheme in ("http", "https"):
            return url

        base_url = extract_base(self.scraper.last_url).strip("/")
        if url.startswith("//"):
            scheme = base_url.split(":")[0]
            return f"{scheme}:{url}"

        if url.startswith("/"):
            return base_url + url

        if not page_url:
            page_url = self.scraper.last_url

        page_url = page_url.rstrip("/")

        if url.startswith("."):
            paths = page_url.split("/")
            parts = url.split("/")
            while parts and (parts[0] == ".." or parts[0] == "."):
                parts = parts[1:]
                if parts[0] == "..":
                    paths = paths[:-1]
            return "/".join(paths + parts)

        return f"{page_url}/{url}"

    def download_image(self, url: str, output_file: Path) -> None:
        """Download an image from the source and save it to the target file."""
        if not url:
            raise LNException("URL is missing")

        if output_file.is_file():
            os.utime(output_file)
            return

        img = self.scraper.get_image(url)
        if img.mode not in ("L", "RGB", "YCbCr", "RGBX"):
            if img.mode == "RGBa":
                img = img.convert("RGBA").convert("RGB")
            else:
                img = img.convert("RGB")

        with atomic_write(output_file) as tmp:
            img.save(tmp, "JPEG", optimized=True)

    def download_cover(self, cover_url: str, cover_file: Path) -> None:
        try:
            self.download_image(cover_url, cover_file)
            ctx.logger.debug(f"Cover saved: {cover_url} -> {cover_file}")
            return
        except Exception as e:
            ctx.logger.warn(
                f"Cover download failed: {cover_url} -> {cover_file}",
                exc_info=ctx.logger.is_debug,
            )
            if not self.auto_generate_cover:
                raise LNException("Failed to download cover") from e

        if cover_file.is_file():
            os.utime(cover_file)
            return

        from ..utils.imgen import generate_cover_image

        img = generate_cover_image()
        with atomic_write(cover_file) as tmp:
            img.save(tmp, "JPEG", optimized=True)
        ctx.logger.debug(f"Cover generated: {cover_file}")

    def format_novel(self, novel: Novel) -> None:
        if not novel.title:
            raise LNException("Novel title is missing")

        crawler_version = getattr(self, "version", None)
        novel.crawler_version = crawler_version

        novel.title = format_title(novel.title)
        novel.author = ", ".join(filter(None, map(format_title, novel.author.split(","))))
        novel.tags = list(filter(None, map(normalize, set(novel.tags or []))))

        total_volumes = len(novel.volumes)
        total_chapters = len(novel.chapters)

        novel.volumes.sort(key=lambda x: x.id)
        novel.chapters.sort(key=lambda x: x.id)

        if total_volumes == 0 and total_chapters > 0:
            total_volumes = math.ceil(total_chapters / self.chapters_per_volume)
            novel.volumes = [Volume(id=i + 1) for i in range(total_volumes)]

        vol_id_map: Dict[int, int] = {}
        for index, volume in enumerate(novel.volumes):
            volume.crawler_version = crawler_version
            vol_id_map[volume.id] = index
            volume.id = index + 1
            volume.chapters = 0
            volume.title = format_title(volume.title) or f"Volume {volume.id}"

        unknown_volume = Volume(
            id=total_volumes + 1,
            title="Unknown",
            crawler_version=crawler_version,
            chapters=0,
        )

        for index, chapter in enumerate(novel.chapters):
            chapter.crawler_version = crawler_version
            chapter.id = index + 1
            chapter.url = HttpUrl(chapter.url).encoded_string()
            chapter.title = format_title(chapter.title) or f"Chapter {chapter.id}"

            if chapter.volume not in vol_id_map:
                chapter.volume = 1 + (index // self.chapters_per_volume)

            vol_index = vol_id_map.get(chapter.volume, -1)
            if vol_index == -1 and novel.volumes[-1] != unknown_volume:
                novel.volumes.append(unknown_volume)

            volume = novel.volumes[vol_index]
            chapter.volume = volume.id
            volume.chapters += 1

    def format_chapter(self, chapter: Chapter) -> None:
        if not chapter.title:
            raise LNException("Chapter title is missing")

        crawler_version = getattr(self, "version", None)
        chapter.crawler_version = crawler_version

        chapter.title = format_title(chapter.title)
        chapter.body = (chapter.body or "").strip()
        chapter.success = bool(chapter.body)
        self._extract_images(chapter)

    def _extract_images(self, chapter: Chapter) -> None:
        chapter.setdefault("images", {})
        if ctx.config.crawler.ignore_images or not chapter.body:
            return

        soup = self.scraper.make_soup(chapter.body)
        for img in soup.select("img[src]"):
            src_url = img.get_attr("src")
            if not src_url:
                continue

            full_url = self.absolute_url(src_url, page_url=chapter.url)
            if not full_url.startswith("http"):
                continue

            id_text = str([chapter.url, full_url])
            image_id = hashlib.md5(id_text.encode()).hexdigest()
            img.attrs = {"src": f"images/{image_id}.jpg", "alt": image_id}
            chapter.images[image_id] = full_url

        if chapter.images:
            chapter.body = soup.body.inner_html
        soup.decompose()
