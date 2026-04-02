from __future__ import annotations

import hashlib
import math
import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from ..context import ctx
from ..exceptions import LNException
from ..utils.imgen import generate_cover_image
from ..utils.text_tools import format_title, normalize
from ..utils.url_tools import extract_base
from .cleaner import TextCleaner
from .models import Chapter, Novel, SearchResult, Volume
from .scraper import Scraper
from .taskman import TaskManager


class Crawler(ABC):
    base_url: Union[str, List[str]]

    language = ""
    has_mtl = False
    has_manga = False

    can_login = False
    can_search = False

    chapters_per_volume = 100
    auto_generate_cover = True

    is_disabled = False
    disable_reason = ""
    version = 0

    # ------------------------------------------------------------------------- #
    # Constructor & Destructors
    # ------------------------------------------------------------------------- #
    def __init__(
        self,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> None:
        """
        Creates a standalone Crawler instance.

        Args:
        - origin (str): The origin URL of the source.
        - workers (int, optional): Number of concurrent workers to expect.
        - parser (Optional[str], optional): Desirable features of the parser. This can be the name of a specific parser
            ("lxml", "lxml-xml", "html.parser", or "html5lib") or it may be the type of markup to be used ("html", "html5", "xml").
        """
        if isinstance(self.base_url, str):
            self.base_url = [self.base_url]
        if not origin or origin not in self.base_url:
            origin = self.base_url[0]

        self.cleaner = TextCleaner()
        self.taskman = TaskManager(workers=workers)
        self.scraper = Scraper(origin=origin, parser=parser)

    def close(self) -> None:
        self.scraper.close()
        self.taskman.close()

    # ------------------------------------------------------------------------- #
    # Methods to implement in crawler
    # ------------------------------------------------------------------------- #

    def initialize(self) -> None:
        pass

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

        base_url = extract_base(self.scraper.last_soup_url).strip("/")
        if url.startswith("//"):
            scheme = base_url.split(":")[0]
            return f"{scheme}:{url}"

        if url.startswith("/"):
            return base_url + url

        if not page_url:
            page_url = self.scraper.last_soup_url

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

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb") as tmp:
            img.save(tmp, "JPEG", optimized=True)
            os.rename(tmp.name, output_file)

    def download_cover(self, cover_url: str, cover_file: Path) -> None:
        try:
            self.download_image(cover_url, cover_file)
            ctx.logger.debug(f"Cover saved: {cover_url} -> {cover_file}")
            return
        except Exception as e:
            if not self.auto_generate_cover:
                raise LNException("Failed to download cover") from e

        if cover_file.is_file():
            os.utime(cover_file)
            return

        img = generate_cover_image()
        cover_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb") as tmp:
            img.save(tmp, "JPEG", optimized=True)
            os.rename(tmp.name, cover_file)
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
        self.extract_images(chapter)

    def extract_images(self, chapter: Chapter) -> None:
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
